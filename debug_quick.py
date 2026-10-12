import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def test():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=5)
    print(f"Fetched {len(markets)} markets")
    for m in markets:
        print(m.question[:80], m.liquidity, m.clob_token_ids)
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book:
            yes_prices = [float(a['price']) for a in yes_book.asks[:3]]
            no_prices = [float(a['price']) for a in no_book.asks[:3]]
            print("  Yes asks:", yes_prices)
            print("  No asks:", no_prices)
            if yes_prices and no_prices:
                total = min(yes_prices)+min(no_prices)
                print("  Sum best asks:", total)

asyncio.run(test())
