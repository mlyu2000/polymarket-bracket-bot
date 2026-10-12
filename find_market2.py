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
            # find minimum price
            yes_min = min(float(a['price']) for a in yes.asks)
            no_min = min(float(a['price']) for a in no.asks)
            print('yes_min', yes_min)
            print('no_min', no_min)
            print('sum', yes_min+no_min)
            break

asyncio.run(find())
