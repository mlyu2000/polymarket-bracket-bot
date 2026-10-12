import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=3)
    for m in markets:
        print("Question:", m.question[:60])
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        # The book for 'No' token has asks on it? Let's see if we swap logic.
        # Actually the book we need is best ask to BUY. For Yes token, ask is sell price.
        # For No token, ask is sell price too.
        # But if no_book has no asks, maybe we need to fetch the opposite?
        # Check bids on no_book
        if no_book and no_book.bids:
            print("  no token bids (sell NO?)", no_book.bids[0])
        if yes_book and yes_book.bids:
            print("  yes token bids", yes_book.bids[0])

asyncio.run(test())
