import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=3)
    for m in markets:
        print(m.question[:80])
        print("clob_token_ids:", m.clob_token_ids)
        print("outcomes:", m.outcomes)
        # Try both orders
        yes_id = m.clob_token_ids[0]
        no_id = m.clob_token_ids[1]
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        print("yes asks:", yes_book.asks[:2] if yes_book else None)
        print("no asks:", no_book.asks[:2] if no_book else None)
        # Also fetch swapped
        yes_book2 = await api.fetch_order_book(no_id)
        no_book2 = await api.fetch_order_book(yes_id)
        print("swapped yes asks:", yes_book2.asks[:2] if yes_book2 else None)
        print("swapped no asks:", no_book2.asks[:2] if no_book2 else None)
        print("---")

asyncio.run(test())
