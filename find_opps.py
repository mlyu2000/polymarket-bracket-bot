import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    opps = []
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.yes_price, opp.no_price, m.question))
    print('found', len(opps))
    for o in opps:
        print(o)

asyncio.run(f())
