import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=1)
    m = markets[0]
    print(m.question)
    print(m.clob_token_ids)
    yes_id, no_id = m.clob_token_ids
    yes_book = await api.fetch_order_book(yes_id)
    no_book = await api.fetch_order_book(no_id)
    print("yes asks:", len(yes_book.asks) if yes_book else None)
    print("yes bids:", len(yes_book.bids) if yes_book else None)
    print("no asks:", len(no_book.asks) if no_book else None)
    print("no bids:", len(no_book.bids) if no_book else None)
    # Try swapped
    yes_book2 = await api.fetch_order_book(no_id)
    no_book2 = await api.fetch_order_book(yes_id)
    print("swapped yes asks:", len(yes_book2.asks) if yes_book2 else None)
    print("swapped no asks:", len(no_book2.asks) if no_book2 else None)

asyncio.run(test())
