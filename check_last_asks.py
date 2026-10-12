import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if "US obtains Iranian enriched uranium by September 30" in m.question:
            yes_id, no_id = m.clob_token_ids
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            print("YES asks last 10:")
            for a in yes_book.asks[-10:]:
                print(a)
            print("NO asks last 10:")
            for a in no_book.asks[-10:]:
                print(a)
            break

asyncio.run(main())
