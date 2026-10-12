import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def debug():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=200)
    count=0
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print("FOUND", opp.total_cost, m.question[:80])
            count+=1
        else:
            if yes_book.asks and no_book.asks:
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price+no_price
                if total<1.001:
                    print("near", total, m.question[:80])
    print("done", count)

asyncio.run(debug())
