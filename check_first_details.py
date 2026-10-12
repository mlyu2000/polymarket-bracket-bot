import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    for i, m in enumerate(markets[:10]):
        if len(m.clob_token_ids) != 2:
            continue
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book:
            continue
        yes_first = yes_book.asks[0] if yes_book.asks else None
        no_first = no_book.asks[0] if no_book.asks else None
        if yes_first and no_first:
            print(i, m.question[:60])
            print(' yes first', yes_first)
            print(' no first', no_first)
            print()

asyncio.run(f())
