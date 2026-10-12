import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

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
    priced = 0
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
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                priced += 1
                # CORRECTED: asks are DESC-sorted in CLOB payload; use min()
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'scan_time': time.time() - t0,
    }

result = asyncio.run(scan())
print(f"Scan(min-ask): {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00 via detector): {len(result['opps'])}")
for o in result['opps']:
    print(f"  [HIT] sum={o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
print(f"Near-misses (<=1.005, best asks): {len(result['near_misses'])}")
for total, q, yp, npr, liq in result['near_misses'][:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
