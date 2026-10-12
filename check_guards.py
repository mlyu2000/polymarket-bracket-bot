import asyncio
from config import Config
from detector import BracketDetector

async def f():
    Config.validate()
    from polymarket_api import PolymarketAPI
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    for m in markets:
        if 'LeBron James' in m.question:
            yes_book = await api.fetch_order_book(m.clob_token_ids[0])
            no_book = await api.fetch_order_book(m.clob_token_ids[1])
            print('Liquidity', m.liquidity)
            print('Min liquidity config', Config.MIN_LIQUIDITY_USDC)
            print('Active', m.active, 'closed', m.closed)
            detector = BracketDetector()
            # check each guard
            print('yes_book', bool(yes_book))
            print('no_book', bool(no_book))
            print('yes asks', bool(yes_book.asks))
            print('no asks', bool(no_book.asks))
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            print('yes price', float(yes_ask['price']))
            print('no price', float(no_ask['price']))
            print('yes vol', float(yes_ask['size']))
            print('no vol', float(no_ask['size']))
            print('total', float(yes_ask['price'])+float(no_ask['price']))
            break

asyncio.run(f())
