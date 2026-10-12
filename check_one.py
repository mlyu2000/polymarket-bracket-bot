import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def check():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=5)
    for m in markets:
        token_pair = (m.clob_token_ids[0], m.clob_token_ids[1])
        books = await api.fetch_order_books_batch([token_pair])
        yes_book, no_book = books[0]
        print("Market:", m.question[:60])
        print("  yes asks:", yes_book.asks[:3] if yes_book else None)
        print("  no asks:", no_book.asks[:3] if no_book else None)
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print(f"  OPPORTUNITY sum={opp.total_cost:.3f} edge={opp.net_edge:.4f}")
        else:
            # debug prices
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                print(f"  best asks yes={yes_price:.3f} no={no_price:.3f} total={total:.3f}")

asyncio.run(check())
