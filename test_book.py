import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    print('market', m.question[:80])
    yes_book = await api.fetch_order_book(m.clob_token_ids[0])
    no_book = await api.fetch_order_book(m.clob_token_ids[1])
    print('yes_book', yes_book.asks[:3] if yes_book and yes_book.asks else None)
    print('no_book', no_book.asks[:3] if no_book and no_book.asks else None)

asyncio.run(test())
