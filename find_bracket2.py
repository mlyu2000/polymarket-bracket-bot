import asyncio
from config import Config
from polymarket_api import PolymarketAPI

async def check():
    Config.validate()
    api = PolymarketAPI()
    # Try liquidity ascending to get markets where brackets might exist
    # Override config sort by manually fetching with different params?
    # For now fetch with volume sort but more markets
    markets = await api.fetch_active_markets(limit=1000)
    print(f"Fetched {len(markets)} markets")
    # Check sums using best ask (last in list)
    count_below = 0
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        # use best ask (last)
        yes_price = float(yes_book.asks[-1]['price'])
        no_price = float(no_book.asks[-1]['price'])
        total = yes_price + no_price
        if total < 1.0:
            print(f"BRACKET: {total:.4f} {m.question[:60]}")
            count_below += 1
    print(f"Brackets found: {count_below}")

asyncio.run(check())
