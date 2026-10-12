import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        print(m.question[:60])
        print('yes asks', yes_book.asks[:3] if yes_book and yes_book.asks else None)
        print('no asks', no_book.asks[:3] if no_book and no_book.asks else None)
        print()

asyncio.run(f())
