import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:70], round(yp,4), round(np_,4), m.liquidity))
    rows.sort()

    tiers = {'<=1.005': 0, '<=1.010': 0, '<=1.020': 0, '<=1.030': 0, '<=1.050': 0}
    for t in tiers:
        tiers[t] = sum(1 for r in rows if r[0] <= float(t[2:]))

    print(f"TIERS: {tiers}")
    print(f"TOP 12 (min-ask sum):")
    for total, q, yp, np_, liq in rows[:12]:
        print(f"  {total:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq {liq:,.0f} | {q}")

    # locate key markets of interest
    for key in ['Atlanta', 'highest temperature']:
        for total, q, yp, np_, liq in rows:
            if key.lower() in q.lower():
                print(f"TRACK[{key}]: {total:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq {liq:,.0f} | {q}")

    out = {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
           'tiers': tiers, 'top15': rows[:15],
           'atl': [(r[0], r[1], r[2], r[3], r[4]) for r in rows if 'atlanta' in r[1].lower()]}
    with open('runs/_tmp_cron_' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime()) + '_tiers.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)

asyncio.run(main())
