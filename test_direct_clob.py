import asyncio
import httpx

async def test():
    token_id = '53509840741650123419298004966458781649613623066147162279506961526018951227575'
    # Use CLOB API via httpx directly
    url = f"https://clob.polymarket.com/book?token_id={token_id}"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        print(resp.status_code)
        print(resp.text[:2000])

asyncio.run(test())
