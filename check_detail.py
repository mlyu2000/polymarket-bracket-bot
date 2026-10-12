import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        print(m.question[:80])
        print(" tokens", m.clob_token_ids)
        print(" outcomes", m.outcomes)
        print()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for i,(yes_book,no_book) in enumerate(all_books):
        print("--- market", i)
        print("yes asks", len(yes_book.asks) if yes_book else None, "bids", len(yes_book.bids) if yes_book else None)
        print("no asks", len(no_book.asks) if no_book else None, "bids", len(no_book.bids) if no_book else None)
        if yes_book and yes_book.asks:
            print(" yes best ask", min(yes_book.asks, key=lambda a: float(a['price'])))
        if no_book and no_book.asks:
            print(" no best ask", min(no_book.asks, key=lambda a: float(a['price'])))

asyncio.run(t())
