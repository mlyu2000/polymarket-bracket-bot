import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor_scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    near = []
    opps = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1.0 or np_ >= 1.0:
            continue
        s = round(yp + np_, 4)
        priced += 1
        rec = [s, m.question[:50], yp, np_, m.liquidity]
        if s < 1.0:
            opps.append(rec)
        elif s <= 1.005:
            near.append(rec)
    near.sort()
    opps.sort()
    floor = min(x[0] for x in near + opps) if (near or opps) else None
    return {'markets': len(markets), 'priced': priced, 'scan_time': time.time() - t0,
            'opps': opps, 'near': near, 'true_floor': floor}

d = asyncio.run(floor_scan())
json.dump(d, open('_tmp_cron_20261008T1602Z_supp_data.json', 'w'), ensure_ascii=False)
print(f"Supp min-ask floor scan: {d['markets']} markets, {d['priced']} priced in {d['scan_time']:.1f}s")
print(f"Sub-1.00 (true brackets): {len(d['opps'])}")
for s, q, yp, np_, liq in d['opps']:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq {liq:.0f} | {q}")
print(f"True floor: {d['true_floor']}")
print(f"Band 1.000-1.005: {len(d['near'])}")
for s, q, yp, np_, liq in d['near'][:8]:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq {liq:.0f} | {q}")
