import asyncio, json, logging, time
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
    scan_time = time.time() - t0

    totals = []
    one_sided = {'yes_only': 0, 'no_only': 0, 'empty': 0, 'both': 0}
    for m, (yb, nb) in zip(markets, all_books):
        has_y = bool(yb and yb.asks)
        has_n = bool(nb and nb.asks)
        if has_y and has_n:
            one_sided['both'] += 1
        elif has_y:
            one_sided['yes_only'] += 1
        elif has_n:
            one_sided['no_only'] += 1
        else:
            one_sided['empty'] += 1
        if not (has_y and has_n):
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        totals.append((round(yp + np_, 4), m.question[:50], round(yp, 4), round(np_, 4), m.liquidity))

    totals.sort()
    tiers = {}
    for t in (1.005, 1.010, 1.020, 1.030, 1.050, 1.100):
        tiers[str(t)] = sum(1 for x in totals if x[0] <= t)
    out = {
        'ts': time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()),
        'markets': len(markets), 'priced': len(totals), 'scan_time': round(scan_time, 1),
        'one_sided': one_sided, 'tiers': tiers,
        'top12': [list(x) for x in totals[:12]],
    }
    fn = f"runs/_tmp_cron_{out['ts']}_tiers.json"
    with open(fn, 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"SCAN {out['ts']}: {out['markets']} mkts / {out['priced']} priced / {out['scan_time']}s")
    print(f"one-sided: {one_sided}")
    print(f"bracketable: {one_sided['both']}/{out['markets']} ({100*one_sided['both']/out['markets']:.1f}%)")
    print(f"TIERS: {tiers}")
    print(f"floor: {totals[0][0]} | {totals[0][1]} (Y@{totals[0][2]} N@{totals[0][3]} liq={totals[0][4]})")
    for t, q, yp, np_, liq in totals[1:12]:
        print(f"  {t:.4f} | Y@{yp} N@{np_} liq={liq} | {q}")
    print(f"artifact: {fn}")


asyncio.run(scan())
