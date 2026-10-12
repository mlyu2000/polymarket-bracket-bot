import asyncio
import httpx

async def test():
    condition_id = '0x7b0f323f4082e1830bf728139ae4b8206fdd9ab979086f7785d8a4f6543f7d70'
    # Try token_id from gamma
    token_id = '64469905005594457751898719080337446869920751709911938125552180158868954986760'
    url = f"https://clob.polymarket.com/orders?token_id={token_id}&limit=5"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url)
        print(resp.status_code)
        print(resp.json()[:500])

asyncio.run(test())
