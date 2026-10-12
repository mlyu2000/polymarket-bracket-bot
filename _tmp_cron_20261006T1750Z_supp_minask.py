import asyncio, logging
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
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(yes_ask["price"]); np_ = float(no_ask["price"])
        rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity,
                     int(float(yes_ask["size"])), int(float(no_ask["size"]))))
    rows.sort()
    return len(markets), rows

n, rows = asyncio.run(scan())
print(f"markets={n} both_sides_priced={len(rows)}")
if rows:
    print(f"TRUE_FLOOR(min-ask)={rows[0][0]:.4f}")
band = [r for r in rows if r[0] <= 1.005]
print(f"band<=1.005 count={len(band)}")
for r in band:
    print(f"  {r[0]:.4f} | yes@{r[2]:.3f}({r[5]}) no@{r[3]:.3f}({r[6]}) | liq={r[4]} | {r[1]}")
print("next-above:")
for r in rows[len(band):len(band)+5]:
    print(f"  {r[0]:.4f} | yes@{r[2]:.3f} no@{r[3]:.3f} | liq={r[4]} | {r[1]}")
