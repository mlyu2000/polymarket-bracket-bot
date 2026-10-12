import asyncio
from config import Config
from polymarket_api import PolymarketAPI
import httpx

async def debug():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if 'Josh Shapiro' in m.question:
            print('Question', m.question)
            print('outcomes', m.outcomes)
            print('outcome_prices', m.outcome_prices)
            print('token ids', m.clob_token_ids)
            yes_id, no_id = m.clob_token_ids
            async with httpx.AsyncClient(timeout=10) as client:
                for token_id, name in [(yes_id, 'token0'), (no_id, 'token1')]:
                    resp = await client.get(f"{Config.CLOB_API_BASE}/book?token_id={token_id}")
                    data = resp.json()
                    print(name, 'asks', data.get('asks')[:2])
                    print(name, 'bids', data.get('bids')[:2])
            break

asyncio.run(debug())
