import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if 'Olympique Lyonnais 0 - 2 Fenerbahçe' in m.question:
            print(m.question)
            print(m.liquidity)
            print(m.clob_token_ids)
            books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yes, no = books[0]
            print('yes asks', yes.asks[:5])
            print('no asks', no.asks[:5])
            break

asyncio.run(find())
