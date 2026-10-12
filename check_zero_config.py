import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    Config.MIN_LIQUIDITY_USDC = 0
    Config.MIN_PROFIT_MARGIN = 0.0001
    Config.FEE_BUFFER = 0
    Config.SLIPPAGE_BUFFER = 0
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    found = []
    for m in markets:
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if not yes_book or not no_book:
            continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            found.append(opp)
    print('found', len(found))
    for o in found:
        print(o.total_cost, o.yes_price, o.no_price, m.question[:60])

asyncio.run(f())
