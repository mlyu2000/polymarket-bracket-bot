import asyncio, json
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    print("Market:", m.question)
    yes_book = await api.fetch_order_book(m.clob_token_ids[0])
    no_book = await api.fetch_order_book(m.clob_token_ids[1])
    print("Yes book raw:", json.dumps(yes_book.__dict__, indent=2))
    print("No book raw:", json.dumps(no_book.__dict__, indent=2))

asyncio.run(test())
