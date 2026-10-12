import asyncio
from config import Config
import httpx

async def check_mapping():
    async with httpx.AsyncClient(timeout=10) as client:
        # get a market
        url = f"{Config.GAMMA_API_BASE}/markets?limit=1&offset=0&active=true&closed=false&order=volume&ascending=false"
        resp = await client.get(url)
        m = resp.json()[0]
        q = m['question']
        outcomes = m.get('outcomes')
        prices = m.get('outcomePrices')
        tokens = m.get('clobTokenIds')
        print('question', q)
        print('outcomes', outcomes)
        print('prices', prices)
        print('tokens', tokens)
        for i, token in enumerate(tokens):
            book_url = f"{Config.CLOB_API_BASE}/book?token_id={token}"
            r = await client.get(book_url)
            data = r.json()
            asks = data.get('asks') or []
            bids = data.get('bids') or []
            print(f'token {i}', 'asks', asks[:1], 'bids', bids[:1])
            # check if market price aligns
            # Actually ask price should be near price for that outcome?
            # The market's outcome price is implied probability
            # If token maps to Yes, then best bid ~ price, best ask ~ price
            # For Yes token, best ask should be high price if Yes is cheap?
            # Let's print
        # Now check condition
        cond_id = m.get('conditionId')
        # fetch condition details?
        print('conditionId', cond_id)

asyncio.run(check_mapping())
