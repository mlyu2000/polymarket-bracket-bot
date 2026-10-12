import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI

# Override config for test
Config.SCAN_SORT_BY = 'liquidity'
Config.MAX_MARKETS_PER_SCAN = 200
Config.MIN_LIQUIDITY_USDC = 100

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    print(f"Fetched {len(markets)} markets in {time.time()-t0:.1f}s")
    brackets = []
    near = []
    for m in markets[:100]:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            total = yp + np
            if total < 1.0:
                brackets.append((total, m.question[:60]))
            elif total <= 1.005:
                near.append((total, m.question[:60]))
    print(f"Brackets: {len(brackets)}, Near: {len(near)}")
    for b in brackets[:5]:
        print("BRACKET", b)
    for n in near[:5]:
        print("NEAR", n)

asyncio.run(scan())
