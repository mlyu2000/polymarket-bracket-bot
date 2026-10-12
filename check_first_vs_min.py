import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1000)
    target = None
    for m in markets:
        if "Alexander Hägg" in m.question:
            target = m
            break
    if not target:
        print("not found")
        return
    yes_book = await api.fetch_order_book(target.clob_token_ids[0])
    no_book = await api.fetch_order_book(target.clob_token_ids[1])
    print("yes first ask:", yes_book.asks[0] if yes_book.asks else None)
    print("yes min ask:", min(yes_book.asks, key=lambda a: float(a['price'])) if yes_book.asks else None)
    print("no first ask:", no_book.asks[0] if no_book.asks else None)
    print("no min ask:", min(no_book.asks, key=lambda a: float(a['price'])) if no_book.asks else None)
    print("first sum:", float(yes_book.asks[0]['price'])+float(no_book.asks[0]['price']))
    print("min sum:", min(float(a['price']) for a in yes_book.asks)+min(float(a['price']) for a in no_book.asks))

asyncio.run(check())
