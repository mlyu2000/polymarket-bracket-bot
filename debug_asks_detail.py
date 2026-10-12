import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets=await api.fetch_active_markets(limit=10)
    for m in markets:
        token_pairs=[(m.clob_token_ids[0], m.clob_token_ids[1])]
        books=await api.fetch_order_books_batch(token_pairs)
        yes_book,no_book=books[0]
        if yes_book and no_book:
            print(m.question[:60])
            print('yes asks[0]', yes_book.asks[0] if yes_book.asks else None)
            print('no asks[0]', no_book.asks[0] if no_book.asks else None)
            yes_min=min(yes_book.asks, key=lambda a: float(a['price'])) if yes_book.asks else None
            no_min=min(no_book.asks, key=lambda a: float(a['price'])) if no_book.asks else None
            print('yes min', yes_min)
            print('no min', no_min)
            print()

asyncio.run(scan())
