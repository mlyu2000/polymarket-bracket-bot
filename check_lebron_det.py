import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    detector = BracketDetector()
    for m in markets:
        if 'LeBron James' in m.question:
            print('Market', m.question)
            print('Liquidity', m.liquidity)
            yes_book = await api.fetch_order_book(m.clob_token_ids[0])
            no_book = await api.fetch_order_book(m.clob_token_ids[1])
            print('Yes asks count', len(yes_book.asks))
            print('No asks count', len(no_book.asks))
            # print min ask price and size
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            print('Best yes', yes_ask)
            print('Best no', no_ask)
            opp = detector.detect(m, yes_book, no_book)
            print('Opp', opp)
            break

asyncio.run(f())
