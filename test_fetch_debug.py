import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    print(f"Fetched {len(markets)} markets")
    for m in markets:
        print(f"{m.question[:80]} | liq={m.liquidity} | tokens={m.clob_token_ids}")
        book_pair = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = book_pair[0]
        if yes_book:
            print(f"  Yes asks: {yes_book.asks[:3]}")
        if no_book:
            print(f"  No asks: {no_book.asks[:3]}")

asyncio.run(test())
