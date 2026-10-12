import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            yp = float(yes_ask['price']); np_ = float(no_ask['price'])
            total = yp + np_
            rows.append((total, yp, np_, m.liquidity, m.question[:70]))
    rows.sort()
    print(f"Markets with two-sided books: {len(rows)}")
    print(f"TRUE floor (min ask+ask): {rows[0][0]:.4f}")
    print("Top 10 cheapest brackets (sum, best-ask basis):")
    for total, yp, np_, liq, q in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"Near-misses <=1.005 (best-ask basis): {len(nm)}")

asyncio.run(scan())
