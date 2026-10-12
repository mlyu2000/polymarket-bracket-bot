import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if "Pogon Szczecin" in m.question:
            print(m.question)
            print(m.liquidity)
            print(m.clob_token_ids)
            books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
            yes_book, no_book = books[0]
            print("yes asks", yes_book.asks[:5] if yes_book else None)
            print("no asks", no_book.asks[:5] if no_book else None)
            if yes_book and yes_book.asks:
                yes_price = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
                print("yes best", yes_price)
            if no_book and no_book.asks:
                no_price = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
                print("no best", no_price)

asyncio.run(t())
