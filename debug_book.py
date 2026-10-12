import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=2)
    m = markets[0]
    print("Market:", m.question)
    print("Tokens:", m.clob_token_ids)
    yes_book = await api.fetch_order_book(m.clob_token_ids[0])
    no_book = await api.fetch_order_book(m.clob_token_ids[1])
    print("Yes book asks first 5:", yes_book.asks[:5])
    print("No book asks first 5:", no_book.asks[:5])
    print("Yes book bids first 5:", yes_book.bids[:5])
    print("No book bids first 5:", no_book.bids[:5])

asyncio.run(test())
