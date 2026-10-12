"""Supplementary: best-ask (min) totals. CLOB /book returns asks DESC-sorted,
so asks[0] in the verbatim near-miss block is the WORST ask (~0.999) and
near-misses there are structurally always 0. detector.py itself correctly uses
min(). This script computes the true best-ask floor across all priced markets
and any brackets/near-misses a fee-aware detector would see."""
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
    dt = time.time() - t0

    priced = 0
    best_opps = []
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        t = yp + np_
        priced += 1
        rows.append((t, m.question[:70], yp, np_, m.liquidity))
        if t < 1.0:
            best_opps.append((t, m.question[:70], yp, np_, m.liquidity))

    rows.sort()
    return {'markets': len(markets), 'priced': priced, 'best_opps': best_opps,
            'rows': rows, 'dt': dt}

r = asyncio.run(scan())
print(f"Markets: {r['markets']} | priced (both books): {r['priced']} | {r['dt']:.1f}s")
print(f"TRUE brackets on best asks (sum<1.00): {len(r['best_opps'])}")
for t, q, yp, np_, liq in r['best_opps']:
    print(f"  🔴 {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print("Top-10 lowest best-ask totals:")
for t, q, yp, np_, liq in r['rows'][:10]:
    flag = " ✅<1.00" if t < 1.0 else (" 📊<=1.005" if t <= 1.005 else "")
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}{flag}")
nm = [x for x in r['rows'] if 1.0 <= x[0] <= 1.005]
print(f"Near-misses on best asks (1.000<=sum<=1.005): {len(nm)}")
le1010 = [x for x in r['rows'] if x[0] <= 1.010]
print(f"Count <=1.010: {len(le1010)}")
with open('_tmp_cron_20261004T0110Z_supp_data.json', 'w') as f:
    json.dump({'floor': r['rows'][0][0] if r['rows'] else None,
               'brackets': len(r['best_opps']),
               'near': len(nm),
               'le1010': len(le1010),
               'top': r['rows'][:10]}, f, default=str)
