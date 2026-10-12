import asyncio
import httpx
async def f():
    async with httpx.AsyncClient() as c:
        r = await c.get('https://clob.polymarket.com/book?token_id=19039930756738455783103072435880506034204446741177886400889371901235212597751')
        d = r.json()
        print(d['asks'][0])
asyncio.run(f())
