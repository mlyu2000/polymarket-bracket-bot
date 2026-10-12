import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api=PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if 'San Francisco 49ers win the 2027' in m.question:
            print('found', m.question, m.liquidity, m.clob_token_ids)
            yes_id, no_id = m.clob_token_ids
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            if yes_book:
                print('yes asks', yes_book.asks[:10])
            if no_book:
                print('no asks', no_book.asks[:10])
            break

asyncio.run(f())
