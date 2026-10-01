import asyncio, logging, time
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
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"Markets with both books: {len(rows)}")
print("Best 10 min-ask sums:")
for total, q, yp, np_, liq in rows[:8]:
    flag = "BRACKET" if total < 1.0 else ("near" if total <= 1.005 else "")
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {flag} | {q}")
print(f"Count sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
print(f"Count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
