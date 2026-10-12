import asyncio, json, logging, os, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    priced = 0
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = round(yp + np_, 6)
        priced += 1
        rec = {'sum': tot, 'q': m.question, 'yes': yp, 'no': np_, 'liq': m.liquidity}
        if tot < 1.0:
            brackets.append(rec)
        rows.append(rec)
    rows.sort(key=lambda r: r['sum'])
    near = [r for r in rows if r['sum'] <= 1.005]
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = {
        'ts': ts,
        'method': 'min-ask',
        'markets': len(markets),
        'priced': priced,
        'scan_seconds': dt,
        'best_min_sum': rows[0]['sum'] if rows else None,
        'brackets': sorted(brackets, key=lambda r: r['sum']),
        'near_le_1005': near,
    }
    os.makedirs('runs', exist_ok=True)
    path = f'runs/cron_scan_{ts}.json'
    with open(path, 'w') as f:
        json.dump(out, f, indent=1)
    print(f"saved {path}")
    print(f"markets={out['markets']} priced={out['priced']} best_min_sum={out['best_min_sum']} brackets={len(out['brackets'])} near<=1.005={len(near)}")
    for r in near[:5]:
        print(f"  {r['sum']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']:.0f} | {r['q'][:55]}")

asyncio.run(scan())
