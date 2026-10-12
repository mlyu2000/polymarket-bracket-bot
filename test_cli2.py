import asyncio
import httpx
async def f():
    async with httpx.AsyncClient() as c:
        r = await c.get('https://clob.polymarket.com/book?token_id=19039930756738455783103072435880506034204446741177886400889371901235212597751')
        d = r.json()
        asks = d['asks']
        print('asks count', len(asks))
        print('first 5', asks[:5])
        print('last 5', asks[-5:])
asyncio.run(f())
