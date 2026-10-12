import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    print("Markets fetched:", len(markets))
    for m in markets:
        print(m.question[:60], m.clob_token_ids)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for i, (yes_book, no_book) in enumerate(all_books):
        print(i, "yes", yes_book is not None, "asks", len(yes_book.asks) if yes_book and yes_book.asks else 0)
        if yes_book and yes_book.asks:
            print("  first ask price", yes_book.asks[0]['price'])
        if no_book and no_book.asks:
            print("  first ask price", no_book.asks[0]['price'])

asyncio.run(check())
