import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def debug_detector():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        books = await api.fetch_order_books_batch([(m.clob_token_ids[0], m.clob_token_ids[1])])
        yes_book, no_book = books[0]
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_price = min(float(a['price']) for a in yes_book.asks)
        no_price = min(float(a['price']) for a in no_book.asks)
        total = yes_price + no_price
        if total < 1.0:
            print("BRACKET FOUND", total, m.question[:80])
            opp = detector.detect(m, yes_book, no_book)
            print("detector", opp)
            break

asyncio.run(debug_detector())
