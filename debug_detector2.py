import asyncio
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from config import Config

async def f():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    detector = BracketDetector()
    for m in markets:
        if len(m.clob_token_ids) != 2:
            continue
        print(m.question[:60], m.liquidity)
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            print(' no book')
            continue
        print(' yes asks', len(yes_book.asks))
        print(' no asks', len(no_book.asks))
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print(' OPPORTUNITY', opp.total_cost, opp.net_edge)
        else:
            # debug
            yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
            no_ask = min(no_book.asks, key=lambda a: float(a['price']))
            print(' best asks', yes_ask, no_ask)
            print(' total', float(yes_ask['price'])+float(no_ask['price']))
        print('---')

asyncio.run(f())
