import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"priced markets: {len(rows)}")
brackets = [r for r in rows if r[0] < 1.0]
print(f"TRUE brackets (min-ask sum < 1.0): {len(brackets)}")
for r in brackets[:10]:
    print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
print("top 5 best sums (min-ask):")
for r in rows[:5]:
    print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
band = [list(r) for r in rows if r[0] <= 1.005]
with open('_tmp_cron_20261010T0508Z_supp_data.json', 'w') as f:
    json.dump({"floor": (rows[0][0] if rows else None), "band": band, "top20": [list(r) for r in rows[:20]]}, f)
