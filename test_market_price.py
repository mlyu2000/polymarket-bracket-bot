import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api=PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    print(m.question)
    print('outcome_prices', m.outcome_prices)
    yes_book = await api.fetch_order_book(m.clob_token_ids[0])
    no_book = await api.fetch_order_book(m.clob_token_ids[1])
    print('yes token', m.clob_token_ids[0])
    print('yes asks first 3', yes_book.asks[:3])
    print('no token', m.clob_token_ids[1])
    print('no asks first 3', no_book.asks[:3])
    # bids
    print('yes bids first 3', yes_book.bids[:3])
    print('no bids first 3', no_book.bids[:3])

asyncio.run(f())
