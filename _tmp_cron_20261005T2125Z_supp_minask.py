import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not book.asks:
        return None
    return min(float(a['price']) for a in book.asks)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    priced = 0
    floor = None
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
            yp = best_ask(yes_book)
            np_ = best_ask(no_book)
            if yp is not None and np_ is not None:
                priced += 1
                total = yp + np_
                if floor is None or total < floor[0]:
                    floor = (total, m.question[:50])
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    return {
        'markets': len(markets),
        'priced': priced,
        'opps': opps,
        'near_misses': near_misses,
        'floor': floor,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Scan(best-ask): {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"BRACKETS (sum < 1.00 via detector): {len(result['opps'])}")
for o in result['opps']:
    print(f"  RED sum={o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | {o['q']}")
print(f"Near-misses (min-ask sum <=1.005): {len(result['near_misses'])}")
for total, q, yp, np_, liq in result['near_misses'][:12]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if result['floor']:
    print(f"True floor: {result['floor'][0]:.3f} | {result['floor'][1]}")
