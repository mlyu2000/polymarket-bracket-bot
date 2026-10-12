import asyncio
from polymarket_api import PolymarketAPI

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=100)
    for m in markets[:5]:
        print(m.question[:80], m.liquidity, len(m.clob_token_ids))
        if len(m.clob_token_ids) == 2:
            yes_id, no_id = m.clob_token_ids
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            if yes_book and yes_book.asks:
                print('  yes asks count', len(yes_book.asks))
                print('  yes asks[0]', yes_book.asks[0])
                best = min(yes_book.asks, key=lambda a: float(a['price']))
                print('  yes best', best)
            if no_book and no_book.asks:
                print('  no asks count', len(no_book.asks))
                print('  no asks[0]', no_book.asks[0])
                best = min(no_book.asks, key=lambda a: float(a['price']))
                print('  no best', best)

asyncio.run(f())
