import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def f():
    # override config
    Config.MIN_LIQUIDITY_USDC = 0
    Config.MIN_PROFIT_MARGIN = 0.0001
    Config.FEE_BUFFER = 0
    Config.SLIPPAGE_BUFFER = 0
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    count = 0
    for m, (yb, nb) in zip(markets, books):
        opp = detector.detect(m, yb, nb)
        if opp:
            print('BRACKET', opp.total_cost, m.question[:60])
            count += 1
    print('total brackets', count)

asyncio.run(f())
