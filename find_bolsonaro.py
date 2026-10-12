import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=2000)
    for m in markets:
        if "Michelle Bolsonaro" in m.question:
            print(m.question)
            print(m.clob_token_ids)
            yes_id, no_id = m.clob_token_ids
            api2 = PolymarketAPI()
            yes_book = await api2.fetch_order_book(yes_id)
            no_book = await api2.fetch_order_book(no_id)
            print("yes asks:", yes_book.asks[:10] if yes_book else None)
            print("no asks:", no_book.asks[:10] if no_book else None)
            break

asyncio.run(test())
