import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=3)
    for m in markets:
        print("Question:", m.question[:60])
        print("  outcomes:", m.outcomes)
        print("  outcome_prices:", m.outcome_prices)
        print("  clob_token_ids:", m.clob_token_ids)
        # fetch books
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        print("  token0 asks:", len(yes_book.asks) if yes_book else None, "bids:", len(yes_book.bids) if yes_book else None)
        print("  token1 asks:", len(no_book.asks) if no_book else None, "bids:", len(no_book.bids) if no_book else None)
        if yes_book and yes_book.asks:
            print("  token0 best ask:", yes_book.asks[0])
        if no_book and no_book.asks:
            print("  token1 best ask:", no_book.asks[0])

asyncio.run(test())
