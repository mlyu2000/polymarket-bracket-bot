import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=200)
    print(f"got {len(markets)}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    print(f"books len {len(books)}")
    count_missing = 0
    for i, (yb, nb) in enumerate(books):
        if not yb or not nb:
            count_missing += 1
        elif not yb.asks or not nb.asks:
            count_missing += 1
    print(f"missing {count_missing}")

asyncio.run(test())
