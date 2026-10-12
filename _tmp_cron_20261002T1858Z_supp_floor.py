import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        priced += 1
        rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))

    rows.sort()
    print(f"priced markets: {priced} / {len(markets)}")
    if rows:
        print(f"TRUE FLOOR (min sum of best asks): {rows[0][0]:.4f}")
    print(f"sum < 1.000 (real brackets): {sum(1 for r in rows if r[0] < 1.000)}")
    print(f"sum <= 1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    print("top 10 closest:")
    for total, q, yp, np_, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(supp())
