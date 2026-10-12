import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Markets fetched: {len(markets)}")
    # Check first few for asks
    for i,m in enumerate(markets[:5]):
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if yes_book and yes_book.asks:
            best_ask_price = float(yes_book.asks[-1]['price'])
        else:
            best_ask_price = None
        print(i, m.question[:50], best_ask_price, len(yes_book.asks) if yes_book else 0)

asyncio.run(scan())
