import asyncio
import httpx
async def f():
    async with httpx.AsyncClient() as c:
        r = await c.get('https://clob.polymarket.com/book?token_id=33740164601821693667331453865716790315281818279379504703738279486691357870183')
        d = r.json()
        print('bids', d['bids'][:5])
        print('asks', d['asks'][:5])
asyncio.run(f())
