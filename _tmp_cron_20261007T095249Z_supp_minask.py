import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if total < 1.0:
                brackets.append((total, m.question[:60], yp, np_, m.liquidity))
            elif total <= 1.005:
                rows.append((total, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    brackets.sort()
    return markets, brackets, rows

markets, brackets, rows = asyncio.run(scan())
print(f"MIN-ASK TRUE BRACKETS (sum < 1.00): {len(brackets)}")
for total, q, yp, np_, liq in brackets[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"MIN-ASK NEAR-MISSES (1.00 < sum <= 1.005): {len(rows)}")
for total, q, yp, np_, liq in rows[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
