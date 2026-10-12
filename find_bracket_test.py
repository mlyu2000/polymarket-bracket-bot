import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    count = 0
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
            no_price = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
            total = yes_price + no_price
            if total < 1.0:
                print(f"BRACKET {total:.4f} {m.question[:60]}")
                count+=1
        if count>=5:
            break

asyncio.run(find())
