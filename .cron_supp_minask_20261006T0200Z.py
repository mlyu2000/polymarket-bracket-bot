# Supplemental: correct near-miss floor using BEST asks (min price), not asks[0].
# Polymarket CLOB /book returns asks DESC-sorted, so asks[0] is the worst ask.
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
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    return rows

rows = asyncio.run(scan())
print(f"markets with both books priced: {len(rows)}")
print("--- best-ask floor TOP 12 ---")
for total, q, yp, np_, liq in rows[:12]:
    nm = "  <=1.005 NEAR-MISS" if total <= 1.005 else ""
    br = "  <1.00 BRACKET" if total < 1.0 else ""
    print(f"{total:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}{nm}{br}")
