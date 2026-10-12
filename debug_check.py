import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    print(f"Markets: {len(markets)}")
    for m in markets:
        print(m.question[:60], m.clob_token_ids, m.liquidity)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    for i, (y, n) in enumerate(books):
        print(f"\nMarket {i}")
        print("YES book asks:", y.asks[:3] if y and y.asks else None)
        print("NO book asks:", n.asks[:3] if n and n.asks else None)

asyncio.run(check())
