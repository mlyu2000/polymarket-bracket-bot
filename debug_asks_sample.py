import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    print(f"Fetched {len(markets)} markets")
    for m in markets:
        print("\nMarket:", m.question[:80])
        print("  clob_token_ids:", m.clob_token_ids)
        yes_book = await api.fetch_order_book(m.clob_token_ids[0])
        no_book = await api.fetch_order_book(m.clob_token_ids[1])
        if yes_book and yes_book.asks:
            print("  YES asks:", yes_book.asks[:5])
        if no_book and no_book.asks:
            print("  NO asks:", no_book.asks[:5])

asyncio.run(test())
