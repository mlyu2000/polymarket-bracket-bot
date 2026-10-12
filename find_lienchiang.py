import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for i,m in enumerate(markets):
        if 'Lienchiang' in m.question:
            print('found', i, m.question)
            token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
            books = await api.fetch_order_books_batch(token_pairs)
            yes,no = books[0]
            print('yes asks first 5', yes.asks[:5])
            print('no asks first 5', no.asks[:5])
            # compute min
            yes_min = min(yes.asks, key=lambda a: float(a['price']))
            no_min = min(no.asks, key=lambda a: float(a['price']))
            print('yes min', yes_min)
            print('no min', no_min)
            print('sum first', float(yes.asks[0]['price'])+float(no.asks[0]['price']))
            print('sum min', float(yes_min['price'])+float(no_min['price']))
            break

asyncio.run(find())
