import asyncio
from polymarket_api import PolymarketAPI

async def check():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if 'Lienchiang' in m.question:
            print('market', m.question)
            print('tokens', m.clob_token_ids)
            books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yes, no = books[0]
            print('yes asset', yes.asset_id)
            print('yes asks first 10')
            for a in yes.asks[:10]:
                print(a)
            print('no asset', no.asset_id)
            print('no asks first 10')
            for a in no.asks[:10]:
                print(a)
            break

asyncio.run(check())
