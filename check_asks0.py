import asyncio
from polymarket_api import PolymarketAPI

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=20)
    for m in markets:
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = float(yes_book.asks[0]['price'])
            np = float(no_book.asks[0]['price'])
            print(m.question[:60], yp, np, yp+np)

asyncio.run(main())
