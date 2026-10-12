import asyncio, logging
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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            rows.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    rows.sort()
    print(f"Markets priced: {len(rows)}")
    print("True floor (min-ask sums), lowest 10:")
    for total, q, yp, np_, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    under = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"BRACKETS min-ask (sum < 1.00): {len(under)}")
    for total, q, yp, np_, liq in under:
        print(f"  🔴 {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"Near-misses min-ask (<=1.005): {len(nm)}")

asyncio.run(supp())
