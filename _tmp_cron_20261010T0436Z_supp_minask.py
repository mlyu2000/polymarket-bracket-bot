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
    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        if total < 1.0:
            brackets.append((total, m.question[:70], ya, na, m.liquidity))
        elif total <= 1.005:
            rows.append((total, m.question[:70], ya, na, m.liquidity))
    rows.sort()
    brackets.sort()
    print(f"markets={len(markets)} priced={priced}")
    print(f"TRUE_BRACKETS(min-ask sum<1.000)={len(brackets)}")
    for t, q, ya, na, liq in brackets[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"NEAR_MISS(<=1.005)={len(rows)}")
    for t, q, ya, na, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
