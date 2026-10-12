import httpx, asyncio

async def fetch():
    async with httpx.AsyncClient(timeout=10) as client:
        token = '93052756429483472623557266413816847161870625221389689202917922255741075876234'
        url = f"https://clob.polymarket.com/book?token_id={token}"
        r = await client.get(url)
        data = r.json()
        print('asks first 10:', data['asks'][:10])
        print('asks last 10:', data['asks'][-10:])
        print('bids first 10:', data['bids'][:10])

asyncio.run(fetch())
