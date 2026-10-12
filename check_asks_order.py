import asyncio
from polymarket_api import PolymarketAPI

async def test():
    api = PolymarketAPI()
    token = '57625488326851426026877860047410699759347243980829448371851725740987550442070'
    ob = await api.fetch_order_book(token)
    print('asks count', len(ob.asks))
    prices = [float(a['price']) for a in ob.asks]
    print('min', min(prices), 'max', max(prices))
    print('first 20', ob.asks[:20])

asyncio.run(test())
