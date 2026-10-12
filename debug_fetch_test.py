import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    print(f"markets {len(markets)}")
    for m in markets:
        print(m.question[:80], m.clob_token_ids, m.liquidity)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    print(f"books {len(all_books)}")
    for i,(y,n) in enumerate(all_books):
        print(i, y is not None, n is not None)
        if y:
            print(" yes asks", len(y.asks))
        if n:
            print(" no asks", len(n.asks))

asyncio.run(test())
