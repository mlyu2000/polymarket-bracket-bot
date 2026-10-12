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
    opps=[]
    for m in markets[:200]:
        if m.liquidity<100: continue
        books=await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yb,nb=books[0]
        opp=detector.detect(m, yb, nb)
        if opp:
            opps.append(opp)
    print('brackets detected', len(opps))
    for o in opps[:10]:
        print(o.total_cost, o.net_edge, o.market.question[:60])

asyncio.run(scan())
