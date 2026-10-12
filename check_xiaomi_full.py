import asyncio
from config import Config
import httpx

async def t():
    async with httpx.AsyncClient(timeout=10) as c:
        tokens = ['67980436365592298978574180935713596608721571696370486161525465415913536157569',
                  '102600142334901186530604932219721019137512465325271939098270618927544575853890']
        for i,tok in enumerate(tokens):
            book = await c.get(f"{Config.CLOB_API_BASE}/book?token_id={tok}")
            data = book.json()
            asks = data.get('asks',[])
            bids = data.get('bids',[])
            print(f'token {i} asks count {len(asks)}')
            print('first 5 asks', asks[:5])
            print('last 5 asks', asks[-5:])
            print('first 5 bids', bids[:5])
            print('last 5 bids', bids[-5:])
            print('---')

asyncio.run(t())
