import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    for m in markets[:20]:
        yes_id = m.clob_token_ids[0]
        no_id = m.clob_token_ids[1]
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        print(m.question[:60])
        print(' yes', yes_book is not None, yes_book.asks[:1] if yes_book and yes_book.asks else None)
        print(' no', no_book is not None, no_book.asks[:1] if no_book and no_book.asks else None)
        print()

asyncio.run(f())
