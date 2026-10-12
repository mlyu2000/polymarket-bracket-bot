"""Cron run 20261004T1945Z supplement: mechanism-agnostic min-ask floor.
The verbatim scan's near-miss block uses asks[0], which on the CLOB payload is
the WORST ask (descending sort) and structurally reports 0. detector.py uses
min() and is correct. This supplement measures true best-ask sums over the
same fetch path."""
import asyncio, logging, time, json
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
    minask_near = []
    priced = 0
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({'q': m.question[:60], 'sum': opp.total_cost, 'edge': opp.net_edge,
                         'shares': opp.max_shares, 'liq': m.liquidity})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            priced += 1
            t2 = ya + na
            rows.append((t2, m.question[:55], ya, na, m.liquidity))
            if t2 <= 1.005:
                minask_near.append((t2, m.question[:50], ya, na, m.liquidity))

    rows.sort()
    minask_near.sort()
    return {
        'markets': len(markets), 'opps': opps, 'minask_near': minask_near,
        'priced': priced, 'rows10': rows[:10],
        'count_le_1010': sum(1 for r in rows if r[0] <= 1.010),
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
print(f"Supp scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"Detector BRACKETS: {len(result['opps'])}")
for o in result['opps']:
    print(f"  ** {o['sum']:.4f} edge={o['edge']:.4f} shares={o['shares']} liq={o['liq']} | {o['q']}")
print(f"Both-sides-priced: {result['priced']}")
print(f"Min-ask near-misses (<=1.005): {len(result['minask_near'])}")
for total, q, ya, na, liq in result['minask_near'][:10]:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")
print(f"count sum<=1.010: {result['count_le_1010']}")
print("Lowest 10 min-ask sums (floor):")
for total, q, ya, na, liq in result['rows10']:
    print(f"  {total:.4f} | Yes@{ya:.4f} No@{na:.4f} | liq={liq} | {q}")
with open('_tmp_cron_20261004T1945Z_supp_data.json', 'w') as f:
    json.dump(result, f, default=str)
