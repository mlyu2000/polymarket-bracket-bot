import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes_book, no_book) in zip(markets, all_books):
        if m.question.startswith("US obtains Iranian enriched uranium"):
            print("Market found")
            print(m.liquidity)
            if yes_book and no_book:
                yes_prices = [float(a['price']) for a in yes_book.asks]
                no_prices = [float(a['price']) for a in no_book.asks]
                print("yes min", min(yes_prices), "no min", min(no_prices))
                print("yes first 3", yes_book.asks[:3])
                print("no first 3", no_book.asks[:3])
            break

asyncio.run(main())
