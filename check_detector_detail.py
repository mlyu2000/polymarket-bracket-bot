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
            yes_volume = int(float(yes_ask["size"]))
            no_volume = int(float(no_ask["size"]))
            max_shares = min(yes_volume, no_volume)
            total_cost = yes_price + no_price
            gross_edge = 1.00 - total_cost
            net_edge = gross_edge - Config.FEE_BUFFER - Config.SLIPPAGE_BUFFER
            print(f"yes_price={yes_price}, no_price={no_price}")
            print(f"yes_volume={yes_volume}, no_volume={no_volume}")
            print(f"max_shares={max_shares}")
            print(f"total_cost={total_cost}")
            print(f"gross_edge={gross_edge}")
            print(f"net_edge={net_edge}")
            print(f"MIN_PROFIT_MARGIN={Config.MIN_PROFIT_MARGIN}")
            break

asyncio.run(test())
