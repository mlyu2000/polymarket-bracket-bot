import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if 'Olympique Lyonnais 0 - 2 Fenerbahçe' in m.question:
            print(m.question)
            books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yes, no = books[0]
            print('yes asks first 20')
            for a in yes.asks[:20]:
                print(a)
            print('no asks first 20')
            for a in no.asks[:20]:
                print(a)
            break

asyncio.run(find())
