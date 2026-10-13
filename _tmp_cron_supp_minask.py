import asyncio, json, time
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    one_sided = {'yes_only': 0, 'no_only': 0, 'empty': 0, 'both': 0}
    priced = []   # (floor, q, ymin, nmin, liq) for two-sided markets
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
            continue
        if has_y and has_n:
            ymin = min(float(a['price']) for a in yb.asks)
            nmin = min(float(a['price']) for a in nb.asks)
            priced.append((ymin + nmin, m.question[:60], ymin, nmin, m.liquidity))

    priced.sort()
    med = priced[len(priced)//2][0] if priced else None
    tiers = {}
    for lim in (1.005, 1.010, 1.020, 1.030, 1.050, 1.100):
        tiers[f'le{lim}'] = sum(1 for p in priced if p[0] <= lim)

    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = {
        'ts': ts, 'markets': len(markets), 'priced': len(priced),
        'scan_time': round(scan_time, 1),
        'one_sided': one_sided,
        'median': med,
        'floor': priced[0][0] if priced else None,
        'floor_q': priced[0][1] if priced else None,
        'floor_yes': priced[0][2] if priced else None,
        'floor_no': priced[0][3] if priced else None,
        'floor_liq': priced[0][4] if priced else None,
        'band': [[round(p[0], 4), p[1], p[2], p[3], round(p[4], 2)] for p in priced[:10]],
        'tiers': tiers,
    }
    with open(f'runs/_tmp_cron_{ts}_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

asyncio.run(main())
