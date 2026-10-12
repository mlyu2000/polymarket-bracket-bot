import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    filtered = [m for m in markets if m.liquidity >= Config.MIN_LIQUIDITY_USDC]
    print('filtered', len(filtered))
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in filtered]
    books = await api.fetch_order_books_batch(token_pairs)
    count = 0
    for m,(yes,no) in zip(filtered, books):
        if not yes or not no or not yes.asks or not no.asks:
            continue
        yes_ask = min(yes.asks, key=lambda a: float(a['price']))
        no_ask = min(no.asks, key=lambda a: float(a['price']))
        total = float(yes_ask['price'])+float(no_ask['price'])
        if total < 1.0:
            count +=1
            print(m.question[:60], total, yes_ask, no_ask)
        elif total < 1.0001:
            count +=1
            print('near', m.question[:60], total)
    print('total', count)

asyncio.run(check())
