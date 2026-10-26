import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    for m in markets:
        q = m.question
        if 'NFL regular' in q and any(t in q for t in ['Falcons', 'Panthers', 'Steelers', 'Broncos', 'Jaguars']):
            print(f"{q[:60]:60s} liq={m.liquidity!r}")

asyncio.run(main())
