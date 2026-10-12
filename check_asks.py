import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    both_asks = 0
    one_ask = 0
    none = 0
    for yes_book, no_book in all_books:
        has_yes = bool(yes_book and yes_book.asks)
        has_no = bool(no_book and no_book.asks)
        if has_yes and has_no:
            both_asks += 1
        elif has_yes or has_no:
            one_ask += 1
        else:
            none += 1
    print("both", both_asks, "one", one_ask, "none", none)

asyncio.run(t())
