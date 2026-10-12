import asyncio, json, logging, time
from datetime import datetime, timezone
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

    rows = []
    priced = 0
    brackets = []
    detector_opps = []
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            detector_opps.append({'q': m.question[:60], 'sum': opp.total_cost, 'edge': opp.net_edge})
        if not (yb and nb and yb.asks and nb.asks):
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        priced += 1
        if tot < 1.0:
            brackets.append({'sum': tot, 'q': m.question[:60], 'yes': yp, 'no': np_, 'liq': m.liquidity})
        rows.append({'sum': tot, 'q': m.question[:55], 'yes': yp, 'no': np_, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    near = [r for r in rows if r['sum'] <= 1.005]
    return {
        'markets': len(markets), 'priced': priced, 'dt': dt,
        'detector_opps': detector_opps, 'brackets': brackets,
        'near_le_1005': near, 'best_min_sum': rows[0]['sum'] if rows else None,
    }

r = asyncio.run(scan())
ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
out = {
    'ts': ts, 'method': 'min-ask',
    'markets': r['markets'], 'priced': r['priced'], 'scan_seconds': r['dt'],
    'best_min_sum': r['best_min_sum'],
    'detector_brackets': r['detector_opps'],
    'brackets': r['brackets'],
    'near_le_1005': r['near_le_1005'],
}
path = f'runs/cron_scan_{ts}.json'
with open(path, 'w') as f:
    json.dump(out, f, indent=1)
print(f"saved {path}")
print(f"markets={r['markets']} priced={r['priced']} time={r['dt']:.1f}s")
print(f"detector brackets: {len(r['detector_opps'])} | min-ask brackets: {len(r['brackets'])}")
print(f"best_min_sum={r['best_min_sum']} near<=1.005 count={len(r['near_le_1005'])}")
for b in r['brackets'][:10]:
    print(f"  BRACKET sum={b['sum']:.4f} Yes@{b['yes']:.3f} No@{b['no']:.3f} liq={b['liq']} | {b['q']}")
for n in r['near_le_1005'][:5]:
    print(f"  {n['sum']:.4f} | Yes@{n['yes']:.3f} No@{n['no']:.3f} | liq={n['liq']} | {n['q']}")
