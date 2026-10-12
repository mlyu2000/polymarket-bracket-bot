import httpx, asyncio

async def fetch():
    async with httpx.AsyncClient(timeout=10) as client:
        token = '107085958393274135120184725550183304311012784782464531533907573867404375561767'
        url = f"https://clob.polymarket.com/book?token_id={token}"
        r = await client.get(url)
        data = r.json()
        asks = data['asks']
        print('num asks', len(asks))
        print('first 3', asks[:3])
        print('last 3', asks[-3:])
        bids = data['bids']
        print('num bids', len(bids))
        print('first 3 bids', bids[:3])
        print('last 3 bids', bids[-3:])

asyncio.run(fetch())
