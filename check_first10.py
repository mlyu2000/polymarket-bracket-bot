import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def find():
    Config.SCAN_SORT_BY = 'volume'
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)} markets")
    for m in markets[:10]:
        print(m.liquidity, m.volume, m.question[:60])
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets[:10]]
    books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes_book, no_book) in zip(markets[:10], books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            print(f"total {total:.4f} yes {yes_price:.3f} no {no_price:.3f} {m.question[:60]}")

asyncio.run(find())
