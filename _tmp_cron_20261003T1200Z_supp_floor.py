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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"rows_with_books: {len(rows)}")
print(f"floor: {rows[0][0]!r}  ceiling-closest5:")
for t, q, yp, np_, liq in rows[:5]:
    print(f"  {t!r} | Yes@{yp} No@{np_} | liq={liq} | {q}")
print(f"count sum<1.0: {sum(1 for r in rows if r[0] < 1.0)}")
print(f"count 1.0<=sum<=1.005: {sum(1 for r in rows if 1.0 <= r[0] <= 1.005)}")
