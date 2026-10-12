import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    Config.validate()
    api = PolymarketAPI()
    m = await api.fetch_active_markets(limit=1)
    print(m[0].question)
    print(m[0].clob_token_ids)
    print(m[0].liquidity)
    book = await api.fetch_order_book(m[0].clob_token_ids[0])
    print(book)
    print(book.asks[:2] if book else None)

asyncio.run(f())
