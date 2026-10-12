import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        # CLOB asks are DESC-sorted -> best ask is the min by price
        ya = min(yes_book.asks, key=lambda a: float(a['price']))
        na = min(no_book.asks, key=lambda a: float(a['price']))
        yp, np_ = float(ya['price']), float(na['price'])
        ys, ns = float(ya.get('size', 0) or 0), float(na.get('size', 0) or 0)
        rows.append((yp + np_, yp, np_, ys, ns, m.question[:58], m.liquidity))

    rows.sort()
    print(f"Markets: {len(markets)} | priced best-ask pairs: {priced}")
    print("TRUE FLOOR (min sum):", f"{rows[0][0]:.4f}" if rows else "n/a")
    print("\nTop 10 lowest best-ask sums:")
    for total, yp, np_, ys, ns, q, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f}(sz {ys:.0f}) No@{np_:.3f}(sz {ns:.0f}) | liq {liq} | {q}")
    print(f"\nsum < 1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"sum <= 1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    print(f"sum <= 1.01: {sum(1 for r in rows if r[0] <= 1.01)}")

asyncio.run(supp())
