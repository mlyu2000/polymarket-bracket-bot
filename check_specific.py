import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

Config.SCAN_SORT_BY='volume'
Config.MAX_MARKETS_PER_SCAN=500
Config.MIN_LIQUIDITY_USDC=100

async def scan():
    api=PolymarketAPI()
    detector=BracketDetector()
    markets=await api.fetch_active_markets()
    # Check specific market
    for m in markets:
        if 'US obtains Iranian' in m.question:
            print('Found market', m.question, m.liquidity)
            books=await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yb,nb=books[0]
            if yb and nb:
                print('yes asks', [float(a['price']) for a in yb.asks[:5]])
                print('no asks', [float(a['price']) for a in nb.asks[:5]])
                yp=min(float(a['price']) for a in yb.asks)
                np=min(float(a['price']) for a in nb.asks)
                print('min total', yp+np)
                opp=detector.detect(m, yb, nb)
                print('opp', opp)
            break

asyncio.run(scan())
