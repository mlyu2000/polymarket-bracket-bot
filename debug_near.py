import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def debug():
    Config.validate()
    api = PolymarketAPI()
    # try liquidity sort with low liquidity
    Config.MIN_LIQUIDITY_USDC = 0
    markets = await api.fetch_active_markets(limit=200)
    print(f"Fetched {len(markets)} markets")
    sums = []
    for m in markets[:100]:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            if total <= 1.005:
                sums.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    sums.sort()
    for s in sums[:20]:
        print(s)

asyncio.run(debug())
