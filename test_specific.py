import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    target = None
    for m in markets:
        if "US obtains Iranian enriched uranium" in m.question:
            target = m
            break
    if not target:
        print("not found")
        return
    print(target.question)
    books = await api.fetch_order_books_batch([(target.clob_token_ids[0], target.clob_token_ids[1])])
    yes_book, no_book = books[0]
    print("yes asks first 5:", yes_book.asks[:5])
    print("no asks first 5:", no_book.asks[:5])
    yes_min = min(float(a['price']) for a in yes_book.asks)
    no_min = min(float(a['price']) for a in no_book.asks)
    print("min yes", yes_min, "min no", no_min, "sum", yes_min+no_min)
    print("first yes", float(yes_book.asks[0]['price']), "first no", float(no_book.asks[0]['price']), "sum", float(yes_book.asks[0]['price'])+float(no_book.asks[0]['price']))

asyncio.run(test())
