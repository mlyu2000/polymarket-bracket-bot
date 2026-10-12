import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    Config.MIN_PROFIT_MARGIN = 0.0
    Config.FEE_BUFFER = 0.0
    Config.SLIPPAGE_BUFFER = 0.0
    Config.MIN_LIQUIDITY_USDC = 0.0
    api=PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    print('markets fetched', len(markets))
    for m in markets:
        # skip if liquidity too low? we set 0
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a['price']))
        no_ask = min(no_book.asks, key=lambda a: float(a['price']))
        total = float(yes_ask['price']) + float(no_ask['price'])
        if total < 1:
            print('BRACKET', total, m.question[:100], yes_ask['price'], no_ask['price'])
            return
    print('no bracket')

asyncio.run(f())
