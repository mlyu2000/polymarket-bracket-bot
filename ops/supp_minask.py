import asyncio, logging, time, json, datetime
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    two_sided = 0
    for m, (yb, nb) in zip(markets, all_books):
        yasks = yb.asks if yb else []
        nasks = nb.asks if nb else []
        if yasks and nasks:
            two_sided += 1
            ymin = min(float(a['price']) for a in yasks)
            nmin = min(float(a['price']) for a in nasks)
            total = ymin + nmin
            rows.append((total, m.question[:70], ymin, nmin, m.liquidity))
    rows.sort()
    floor = rows[0] if rows else None
    bands = {
        'le_1.005': sum(1 for r in rows if r[0] <= 1.005),
        'le_1.010': sum(1 for r in rows if r[0] <= 1.010),
        'le_1.020': sum(1 for r in rows if r[0] <= 1.020),
        'le_1.030': sum(1 for r in rows if r[0] <= 1.030),
        'le_1.050': sum(1 for r in rows if r[0] <= 1.050),
    }
    return {
        'ts': datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'),
        'markets': len(markets),
        'two_sided': two_sided,
        'floor': floor,
        'bands': bands,
        'top10': rows[:10],
    }

r = asyncio.run(supp())
print(json.dumps({k: v for k, v in r.items() if k != 'top10'}, default=str))
print('TOP10:')
for t, q, y, n, liq in r['top10']:
    print(f"  {t:.4f} | Y@{y:.3f} N@{n:.3f} | liq~{liq} | {q}")
with open(f"runs/_tmp_cron_{r['ts']}_supp_data.json", 'w') as f:
    json.dump(r, f, default=str, indent=2)
print('saved: runs/_tmp_cron_' + r['ts'] + '_supp_data.json')
