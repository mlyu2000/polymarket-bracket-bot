import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    diag = {'min_asks': [], 'tiers': {'le1.005': 0, 'le1.010': 0, 'le1.020': 0, 'le1.050': 0, 'lt1.000': 0}}
    two_sided = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        two_sided += 1
        yp = min(float(a['price']) for a in yes_book.asks)
        npx = min(float(a['price']) for a in no_book.asks)
        t = yp + npx
        diag['min_asks'].append((round(t, 4), m.question[:60], round(yp, 4), round(npx, 4), m.liquidity))
        for k, thr in [('le1.005', 1.005), ('le1.010', 1.010), ('le1.020', 1.020), ('le1.050', 1.050), ('lt1.000', 1.0)]:
            if t <= thr if k != 'lt1.000' else t < thr:
                diag['tiers'][k] += 1

    diag['min_asks'].sort()
    print(f"two-sided: {two_sided}/{len(markets)} ({(1 - two_sided/len(markets))*100:.1f}% not bracketable)")
    print(f"tiers: {diag['tiers']}")
    print("top-8 by min-ask:")
    for t, q, yp, npx, liq in diag['min_asks'][:8]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{npx:.3f} | liq {liq:,.0f} | {q}")
    return {'near_misses': [], 'diag': diag, 'two_sided': two_sided}

result = asyncio.run(scan())
with open('runs/_tmp_cron_20261015T1433Z_supp_data.json', 'w') as f:
    json.dump(result, f, default=str)
print("saved runs/_tmp_cron_20261015T1433Z_supp_data.json")
