import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
priced = len(rows)
brackets = [r for r in rows if r[0] < 1.0]
nms = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"priced markets: {priced}")
print(f"true brackets (min-ask sum < 1.0): {len(brackets)}")
for r in brackets[:10]:
    print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
print(f"near-misses (1.0 <= sum <= 1.005): {len(nms)}")
for r in nms[:10]:
    print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
if rows:
    print(f"floor: {rows[0][0]:.4f}")
