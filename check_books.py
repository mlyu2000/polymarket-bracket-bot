import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    print("markets", len(markets))
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for i,(yes_book,no_book) in enumerate(all_books):
        print(i, bool(yes_book), bool(no_book))
        if yes_book:
            print(" yes asks", len(yes_book.asks))
        if no_book:
            print(" no asks", len(no_book.asks))

asyncio.run(t())
