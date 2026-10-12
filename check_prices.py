import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        print("Market:", m.question[:60])
        print(" yes asks:", yes_book.asks[:2] if yes_book else None)
        print(" no asks:", no_book.asks[:2] if no_book else None)
        if yes_book and no_book:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            print(" best sum:", yes_price + no_price)
        print()

asyncio.run(main())
