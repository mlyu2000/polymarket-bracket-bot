import asyncio
from config import Config
import httpx

async def check():
    async with httpx.AsyncClient(timeout=10) as c:
        # get market
        r = await c.get(f"{Config.GAMMA_API_BASE}/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false")
        m = r.json()[0]
        print('question', m['question'][:80])
        print('outcomes', m['outcomes'])
        print('prices', m['outcomePrices'])
        tokens = m['clobTokenIds']
        for i,t in enumerate(tokens):
            book = await c.get(f"{Config.CLOB_API_BASE}/book?token_id={t}")
            data = book.json()
            bids = data.get('bids',[])
            asks = data.get('asks',[])
            best_bid = float(bids[0]['price']) if bids else None
            best_ask = float(asks[0]['price']) if asks else None
            print(f'token {i} best_bid {best_bid} best_ask {best_ask}')

asyncio.run(check())
