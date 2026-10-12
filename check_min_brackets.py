import asyncio
from config import Config
from polymarket_api import PolymarketAPI

Config.SCAN_SORT_BY='volume'
Config.MAX_MARKETS_PER_SCAN=500
Config.MIN_LIQUIDITY_USDC=100

async def find():
    api=PolymarketAPI()
    markets=await api.fetch_active_markets()
    found=[]
    for m in markets[:200]:
        if m.liquidity<100: continue
        books=await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yb,nb=books[0]
        if yb and nb and yb.asks and nb.asks:
            yp=min(float(a['price']) for a in yb.asks)
            np=min(float(a['price']) for a in nb.asks)
            total=yp+np
            if total<1.0:
                found.append((total, m.question[:60]))
            elif total<=1.005:
                found.append((total, m.question[:60]))
    print('found', len(found))
    for f in found[:20]:
        print(f)

asyncio.run(find())
