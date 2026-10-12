from polymarket_api import PolymarketAPI
import asyncio

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    yes_id = m.clob_token_ids[0]
    book = await api.fetch_order_book(yes_id)
    print('market', m.question[:60])
    print('token', yes_id)
    print('bids count', len(book.bids))
    print('asks count', len(book.asks))
    print('bids first 3', book.bids[:3])
    print('bids last 3', book.bids[-3:])
    print('asks first 3', book.asks[:3])
    print('asks last 3', book.asks[-3:])

asyncio.run(f())
