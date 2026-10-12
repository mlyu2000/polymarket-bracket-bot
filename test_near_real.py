import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    near_list = []
    for m in markets:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
            no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
            total_cost = float(yes_ask["price"]) + float(no_ask["price"])
            if total_cost <= 1.005:
                near_list.append((total_cost, m.question[:60], float(yes_ask["price"]), float(no_ask["price"]), m.liquidity))
    near_list.sort()
    for t,q,yp,np,liq in near_list[:20]:
        print(f"{t:.4f} | Yes@{yp:.3f} No@{np:.3f} | {q}")

asyncio.run(test())
