"""Which BTC/Bitcoin-priced markets remain in the active 500?
The 'above $72,000 on October 16' market (sole floor leader at 23:37Z, 1.001)
is absent from the 23:52Z active set."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)


async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    hits = [m for m in markets if any(k in m.question.lower() for k in
            ('bitcoin', 'btc', '$72', '72,000', '72k'))]
    print(f"active={len(markets)} hits={len(hits)}")
    for m in hits:
        print(f"  {m.question[:90]!r} liq={m.liquidity}")


asyncio.run(main())
