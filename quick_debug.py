import asyncio
from config import Config
from polymarket_api import PolymarketAPI

Config.validate()
api = PolymarketAPI()

async def test():
    markets = await api.fetch_active_markets(limit=3)
    for m in markets:
        print('Market:', m.question[:80])
        print('  liquidity', m.liquidity)
        print('  tokens', m.clob_token_ids)
        pair = (m.clob_token_ids[0], m.clob_token_ids[1])
        books = await api.fetch_order_books_batch([pair])
        yes, no = books[0]
        print('  yes asks count', len(yes.asks) if yes else None)
        print('  no asks count', len(no.asks) if no else None)
        if yes and yes.asks:
            print('  yes best ask', yes.asks[0])
        if no and no.asks:
            print('  no best ask', no.asks[0])

asyncio.run(test())
