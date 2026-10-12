import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    # override sort for test
    original_sort = Config.SCAN_SORT_BY
    # Use liquidity ascending to find brackets
    # Can't change class var easily, just fetch with manual params
    # We'll just fetch markets with liquidity sort by changing config temporarily via env? Simpler: fetch via API directly
    # Let's just brute force with current config but print some stats
    markets = await api.fetch_active_markets()
    print(f"Fetched {len(markets)} markets")
    # sample first 20 sums
    for i,m in enumerate(markets[:20]):
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = float(yes_book.asks[-1]['price'])
            no_price = float(no_book.asks[-1]['price'])
            total = yes_price + no_price
            print(i, total, yes_price, no_price, m.question[:50], m.liquidity)

asyncio.run(scan())
