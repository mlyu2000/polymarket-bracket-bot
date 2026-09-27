"""Supplement: same scan but near-misses computed from BEST (min) asks,
since CLOB /book asks are DESC-sorted and asks[0] is the worst ask.
Also reports the best-ask floor across all priced markets."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

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
                'q': m.question[:60], 'yes': opp.yes_price, 'no': opp.no_price,
                'sum': opp.total_cost, 'edge': opp.net_edge,
                'shares': opp.max_shares, 'liq': m.liquidity,
            })
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if floor is None or total < floor:
                floor = total
            if total <= 1.005:
                near_misses.append((round(total, 4), m.question[:50], yp, np, m.liquidity))

    near_misses.sort()
    return {'markets': len(markets), 'priced': priced, 'opps': opps,
            'near_misses': near_misses, 'floor': floor, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"Scan: {result['markets']} markets ({result['priced']} priced) in {result['scan_time']:.1f}s")
print(f"BRACKETS (detector, net_edge>=margin): {len(result['opps'])}")
for o in result['opps']:
    print(f"  ** {o['sum']:.4f} edge={o['edge']:.4f} Yes@{o['yes']:.3f} No@{o['no']:.3f} {o['shares']}sh liq={o['liq']:.0f} | {o['q']}")
print(f"Best-ask floor: {result['floor']}")
print(f"Near-misses (min-ask sum <= 1.005): {len(result['near_misses'])}")
for t, q, yp, np, liq in result['near_misses'][:8]:
    print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
