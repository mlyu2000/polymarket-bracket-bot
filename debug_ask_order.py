import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    near_min = 0
    near_first = 0
    for m,(y,n) in zip(markets, all_books):
        if y and n and y.asks and n.asks:
            # min
            yes_min = min(y.asks, key=lambda a: float(a["price"]))
            no_min = min(n.asks, key=lambda a: float(a["price"]))
            total_min = float(yes_min["price"])+float(no_min["price"])
            if total_min <= 1.005:
                near_min += 1
            # first
            total_first = float(y.asks[0]["price"])+float(n.asks[0]["price"])
            if total_first <= 1.005:
                near_first += 1
    print("near min", near_min)
    print("near first", near_first)

asyncio.run(test())
