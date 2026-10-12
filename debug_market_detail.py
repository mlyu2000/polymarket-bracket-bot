import asyncio
from polymarket_api import PolymarketAPI

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        print(m.id, m.question[:60], m.active, m.closed, m.liquidity, m.clob_token_ids)
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if yes_book and no_book:
            yes_min = min(yes_book.asks, key=lambda a: float(a['price']))
            no_min = min(no_book.asks, key=lambda a: float(a['price']))
            print(' yes min', yes_min)
            print(' no min', no_min)
            print(' sum', float(yes_min['price'])+float(no_min['price']))

asyncio.run(main())
