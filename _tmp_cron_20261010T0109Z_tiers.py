import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks and m.liquidity > 0:
            yp = min(float(a['price']) for a in yb.asks)
            npr = min(float(a['price']) for a in nb.asks)
            rows.append((yp + npr, m.question[:55], yp, npr, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"priced={len(rows)}")
for r in rows[:10]:
    print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {r[1]}")
with open('_tmp_cron_20261010T0109Z_tiers.json','w') as f:
    json.dump([list(r) for r in rows[:15]], f)
