import asyncio
from polymarket_api import PolymarketAPI

async def t():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    count=0
    for m,(yes_book,no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = float(yes_book.asks[0]['price'])
            no_price = float(no_book.asks[0]['price'])
            total = yes_price + no_price
            if total <= 1.01:
                count+=1
                print(f"{total:.4f} asks0 {m.question[:60]}")
    print("count", count)

asyncio.run(t())
