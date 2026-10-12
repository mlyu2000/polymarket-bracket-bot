import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    total_asks=0
    both=0
    for yes_book,no_book in all_books:
        y_has = bool(yes_book and yes_book.asks)
        n_has = bool(no_book and no_book.asks)
        if y_has:
            total_asks+=1
        if n_has:
            total_asks+=1
        if y_has and n_has:
            both+=1
    print("both", both, "total_asks", total_asks)

asyncio.run(t())
