import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        print('market', m.question[:50])
        print(' yes asks first', yes_book.asks[0] if yes_book and yes_book.asks else None)
        print(' yes asks last', yes_book.asks[-1] if yes_book and yes_book.asks else None)
        print(' no asks first', no_book.asks[0] if no_book and no_book.asks else None)
        print(' no asks last', no_book.asks[-1] if no_book and no_book.asks else None)
        print()

asyncio.run(f())
