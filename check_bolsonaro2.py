import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes_book, no_book) in zip(markets, all_books):
        if "Michelle Bolsonaro" in m.question:
            yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
            no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
            yes_price = float(yes_ask["price"])
            no_price = float(no_ask["price"])
            print(f"yes_price={yes_price}, no_price={no_price}")
            print(f"yes_ask size={yes_ask['size']}, no_ask size={no_ask['size']}")
            print(f"total={yes_price+no_price}")
            print(f"liquidity={m.liquidity}")
            break

asyncio.run(test())
