# Supplementary: true best-ask (min) floor check, since CLOB asks are DESC-sorted
# and asks[0] in the verbatim near-miss block reports the worst ask (~0.999).
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    brackets = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        if total < 1.0:
            brackets += 1
        rows.append((total, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"priced={len(rows)} brackets(min-ask sum<1.00)={brackets}")
    print("top-10 best-ask sums:")
    for total, q, ya, na, liq in rows[:10]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(main())
