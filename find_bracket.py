import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    count=0
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_min = min(float(a['price']) for a in yes_book.asks)
        no_min = min(float(a['price']) for a in no_book.asks)
        total = yes_min + no_min
        if total < 1.0:
            print(f"BRACKET: {total:.4f} {m.question[:60]} yes={yes_min} no={no_min}")
            count+=1
    print("total brackets", count)

asyncio.run(test())
