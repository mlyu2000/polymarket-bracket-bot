import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    count = 0
    for m, (yes,no) in zip(markets, books):
        if not yes or not no or not yes.asks or not no.asks:
            continue
        # use detector logic
        yes_ask = min(yes.asks, key=lambda a: float(a['price']))
        no_ask = min(no.asks, key=lambda a: float(a['price']))
        total = float(yes_ask['price'])+float(no_ask['price'])
        if total < 1.0:
            count +=1
            print(m.question[:80], total, m.liquidity)
    print('total <1.0', count)

asyncio.run(scan())
