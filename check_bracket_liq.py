import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    # Force liquidity sort
    orig = Config.SCAN_SORT_BY
    Config.SCAN_SORT_BY = 'liquidity'
    markets = await api.fetch_active_markets(limit=200)
    print('markets', len(markets))
    found = 0
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_price = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
        no_price = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
        total = yes_price + no_price
        if total < 1.0:
            print('BRACKET', total, m.question[:80], m.liquidity)
            found+=1
    print('found', found)

asyncio.run(main())
