import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
    books = await api.fetch_order_books_batch(token_pairs)
    yes, no = books[0]
    print('yes asks[0]', yes.asks[0] if yes.asks else None)
    yes_min = min(yes.asks, key=lambda a: float(a['price'])) if yes.asks else None
    no_min = min(no.asks, key=lambda a: float(a['price'])) if no.asks else None
    print('yes min', yes_min)
    print('no min', no_min)
    if yes.asks and no.asks:
        total0 = float(yes.asks[0]['price']) + float(no.asks[0]['price'])
        total_min = float(yes_min['price']) + float(no_min['price'])
        print('total0', total0, 'total_min', total_min)

asyncio.run(check())
