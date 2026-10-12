import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if 'Olympique Lyonnais 0 - 2 Fenerbahçe' in m.question:
            books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yes, no = books[0]
            print('yes asks length', len(yes.asks))
            print('no asks length', len(no.asks))
            # print tail
            print('yes last 10')
            for a in yes.asks[-10:]:
                print(a)
            print('no last 10')
            for a in no.asks[-10:]:
                print(a)
            break

asyncio.run(find())
