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
    no_book_cnt = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            no_book_cnt += 1
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        rows.append((yes_min + no_min, m.question[:60], yes_min, no_min, m.liquidity))
    rows.sort()
    return rows, len(markets), no_book_cnt

rows, total_markets, no_book_cnt = asyncio.run(scan())
brackets = [r for r in rows if r[0] < 1.0]
near = [r for r in rows if 1.0 <= r[0] <= 1.005]
print(f"[min-ask floor check] priced={len(rows)} no-book={no_book_cnt} of {total_markets} markets")
print(f"true brackets (minAskYes+minAskNo < 1.00): {len(brackets)}")
for t, q, yp, np_, liq in brackets[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"near-misses 1.000-1.005: {len(near)}")
for t, q, yp, np_, liq in near[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if rows:
    print(f"overall best (min-ask) sum: {rows[0][0]:.4f}")
