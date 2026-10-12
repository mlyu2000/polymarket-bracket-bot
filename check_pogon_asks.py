import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if "Pogon Szczecin" in m.question:
            print(m.question)
            books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yes_book, no_book = books[0]
            if yes_book and yes_book.asks:
                print("yes asks first", yes_book.asks[0])
                print("yes best", min(yes_book.asks, key=lambda a: float(a['price'])))
            if no_book and no_book.asks:
                print("no asks first", no_book.asks[0])
                print("no best", min(no_book.asks, key=lambda a: float(a['price'])))

asyncio.run(t())
