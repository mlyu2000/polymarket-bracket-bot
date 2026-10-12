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
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        y = min(float(a['price']) for a in yes_book.asks)
        n = min(float(a['price']) for a in no_book.asks)
        rows.append((y + n, m.question[:60], y, n, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"min-ask floor check over {len(rows)} priced markets")
print("BRACKETS (sum<1.00):", sum(1 for r in rows if r[0] < 1.0))
for total, q, y, n, liq in rows[:8]:
    print(f"  {total:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
