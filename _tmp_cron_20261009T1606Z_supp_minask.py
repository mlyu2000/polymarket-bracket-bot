import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    # Corrected near-miss pass: CLOB asks are DESC-sorted, so best ask = min(price)
    priced = 0
    near = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        yes_min = min(float(a['price']) for a in yb.asks)
        no_min = min(float(a['price']) for a in nb.asks)
        total = yes_min + no_min
        if 0 < yes_min < 1 and 0 < no_min < 1:
            priced += 1
            near.append((total, m.question[:50], yes_min, no_min, m.liquidity))
    near.sort()
    return {'markets': len(markets), 'priced': priced, 'near': near, 't': scan_time}

r = asyncio.run(scan())
print(f"Corrected pass: {r['markets']} markets ({r['priced']} priced) in {r['t']:.1f}s")
print("True floor (min-ask sums, top 10):")
for total, q, yp, np, liq in r['near'][:10]:
    flag = " <-- sum<1.00" if total < 1.0 else ""
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}{flag}")
print(f"Count sum<=1.005: {sum(1 for x in r['near'] if x[0] <= 1.005)}")
print(f"Count sum<1.00: {sum(1 for x in r['near'] if x[0] < 1.0)}")
with open('_tmp_cron_20261009T1606Z_supp_data.json', 'w') as f:
    json.dump(r, f)
