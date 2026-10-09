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
    elapsed = time.time() - t0
    rows = []
    priced = 0
    detector_opps = 0
    for m, (yb, nb) in zip(markets, all_books):
        if detector.detect(m, yb, nb):
            detector_opps += 1
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        priced += 1
        rows.append({'sum': yp + np, 'q': m.question[:60], 'yes': yp, 'no': np, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    return {'markets': len(markets), 'priced': priced, 'elapsed': elapsed,
            'detector_opps': detector_opps, 'band': rows[:40]}

out = asyncio.run(scan())
print(f"markets: {out['markets']} | priced(min-ask): {out['priced']} | elapsed: {out['elapsed']:.1f}s | detector_opps: {out['detector_opps']}")
brackets = [r for r in out['band'] if r['sum'] < 1.0]
near = [r for r in out['band'] if 1.0 <= r['sum'] <= 1.005]
print(f"true brackets (<1.00): {len(brackets)}")
for r in brackets[:10]:
    print(f"  {r['sum']:.4f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
print(f"near-misses (1.00-1.005): {len(near)}")
for r in near[:10]:
    print(f"  {r['sum']:.4f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
if out['band']:
    print(f"absolute floor: {out['band'][0]['sum']:.4f} | {out['band'][0]['q']}")

with open('_tmp_cron_20261009T1252Z_supp_data.json', 'w') as f:
    json.dump(out, f)
