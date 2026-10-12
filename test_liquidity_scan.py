import asyncio
from config import Config
from polymarket_api import PolymarketAPI

# Temporarily override sort
Config.SCAN_SORT_BY = 'liquidity'
Config.MAX_MARKETS_PER_SCAN = 500
Config.MIN_LIQUIDITY_USDC = 100

async def test():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets(limit=500)
    print(f"Fetched {len(markets)} markets, first liquidity {markets[0].liquidity if markets else 'none'}")
    brackets = []
    for i, m in enumerate(markets[:200]):
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total < 1.0:
                brackets.append((total, m.question[:60]))
    print(f"Brackets found: {len(brackets)}")
    for b in brackets[:10]:
        print(b)

asyncio.run(test())
