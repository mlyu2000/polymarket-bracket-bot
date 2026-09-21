import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    # CLOB asks are DESC-sorted; asks[0] is the WORST ask. Use true best ask.
    return min(book.asks, key=lambda a: float(a["price"]))

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    floor = None  # overall min sum across priced markets
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
            paper_result = paper.execute(opp)
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(best_ask(yes_book)['price'])
                no_price = float(best_ask(no_book)['price'])
                total = yes_price + no_price
                if floor is None or total < floor[0]:
                    floor = (total, m.question[:50])
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': scan_time,
        'floor': floor,
    }

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00): {len(result['opps'])}")
for o in result['opps']:
    print(f"  RED {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"Near-misses (<=1.005): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:5]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
if result['floor']:
    print(f"Floor (min sum over priced markets): {result['floor'][0]:.3f} | {result['floor'][1]}")
