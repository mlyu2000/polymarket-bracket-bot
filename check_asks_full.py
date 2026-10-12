import asyncio
from polymarket_api import PolymarketAPI

async def run():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    target = "Will the highest temperature in Busan be 28°C on August 23?"
    for m in markets:
        if target in m.question:
            yes_id, no_id = m.clob_token_ids
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            print("yes asks full:", yes_book.asks)
            print("no asks full:", no_book.asks)
            break

asyncio.run(run())
