import asyncio
from config import Config
import httpx

async def t():
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.get(f"{Config.GAMMA_API_BASE}/markets?limit=10&offset=0&active=true&closed=false&order=volume&ascending=false")
        markets = r.json()
        for m in markets:
            if 'Josh Shapiro' in m['question']:
                print('question', m['question'])
                print('outcomes', m['outcomes'])
                print('prices', m['outcomePrices'])
                tokens = m['clobTokenIds']
                tokens = __import__('json').loads(tokens)
                print('tokens', tokens)
                for i,tok in enumerate(tokens):
                    book = await c.get(f"{Config.CLOB_API_BASE}/book?token_id={tok}")
                    data = book.json()
                    print(f'token {i} last_trade_price', data.get('last_trade_price'))
                break

asyncio.run(t())
