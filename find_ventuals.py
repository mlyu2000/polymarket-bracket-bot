import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if "Ventuals FDV" in m.question:
            print("FOUND:", m.question)
            yes_id, no_id = m.clob_token_ids
            yes_book = await api.fetch_order_book(yes_id)
            no_book = await api.fetch_order_book(no_id)
            if yes_book and yes_book.asks:
                print("Yes asks[0]:", yes_book.asks[0])
                print("Yes min:", min(yes_book.asks, key=lambda a: float(a['price'])))
            if no_book and no_book.asks:
                print("No asks[0]:", no_book.asks[0])
                print("No min:", min(no_book.asks, key=lambda a: float(a['price'])))
            break

asyncio.run(test())
