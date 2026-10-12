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
    priced = 0
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        # True best ask = min over ladder (CLOB asks are DESC-sorted)
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total < 1.0:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            rows.append((total, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    brackets.sort()
    return priced, brackets, rows

priced, brackets, rows = asyncio.run(scan())
print(f"Best-ask (min) recheck: {priced} priced markets")
print(f"TRUE BRACKETS (sum<1.00): {len(brackets)}")
for total, q, yp, np_, liq in brackets:
    print(f"  [BRACKET] {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"TRUE NEAR-MISSES (<=1.005): {len(rows)}")
for total, q, yp, np_, liq in rows[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
