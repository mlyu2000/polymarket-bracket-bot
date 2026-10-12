import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def debug_mapping():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if 'Xiaomi' in m.question:
            print('Market id', m.id)
            print('outcomes', m.outcomes)
            print('outcome_prices', m.outcome_prices)
            yes_id, no_id = m.clob_token_ids
            print('yes token', yes_id)
            print('no token', no_id)
            # fetch book raw via httpx
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                for token_id, name in [(yes_id, 'yes'), (no_id, 'no')]:
                    resp = await client.get(f"{Config.CLOB_API_BASE}/book?token_id={token_id}")
                    data = resp.json()
                    print(name, 'bids', data.get('bids')[:2])
                    print(name, 'asks', data.get('asks')[:2])
                    print(name, 'market', data.get('market'))
            break

asyncio.run(debug_mapping())
