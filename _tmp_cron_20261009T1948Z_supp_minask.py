# Supplement: correct near-miss floor using min asks (asks are DESC-sorted;
# asks[0] in the verbatim script is the worst ask, so its near-miss list is
# always empty). Mirrors detector.py's min() logic.
import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        t = yp + np_
        priced += 1
        rows.append((t, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    print(f"priced markets (min-ask): {priced}/{len(markets)}")
    print("best 8 min-ask totals:")
    for t, q, yp, np_, liq in rows[:8]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"min-ask sum <=1.00: {sum(1 for r in rows if r[0] <= 1.0)}")
    print(f"min-ask sum <=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    json.dump({'markets': len(markets), 'priced': priced, 'near': rows,
               't': None}, open('_tmp_cron_20261009T1948Z_supp_data.json', 'w'))

import time
t0 = time.time()
asyncio.run(main())
d = json.load(open('_tmp_cron_20261009T1948Z_supp_data.json'))
d['t'] = time.time() - t0
json.dump(d, open('_tmp_cron_20261009T1948Z_supp_data.json', 'w'))
print(f"supp time: {d['t']:.1f}s")
