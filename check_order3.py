import asyncio, httpx
async def f():
    async with httpx.AsyncClient() as c:
        r = await c.get('https://clob.polymarket.com/book?token_id=11764339491635950680058502138624743331703264110538822930935866110119325236821')
        d = r.json()
        asks = d['asks']
        print(asks)
asyncio.run(f())
