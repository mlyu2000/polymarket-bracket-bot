import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=10)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m,(yes_book,no_book) in zip(markets, all_books):
        print(m.question[:60])
        if yes_book and yes_book.asks:
            print(" yes asks[0]", yes_book.asks[0])
        if no_book and no_book.asks:
            print(" no asks[0]", no_book.asks[0])

asyncio.run(t())
