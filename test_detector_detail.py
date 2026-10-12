import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=10)
    for m in markets:
        yes_id, no_id = m.clob_token_ids
        yes_book = await api.fetch_order_book(yes_id)
        no_book = await api.fetch_order_book(no_id)
        opp = detector.detect(m, yes_book, no_book)
        print(m.question[:80])
        if yes_book and no_book:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            print(f"  min sum: {yes_price+no_price:.3f}")
            print(f"  best ask sum (first): {float(yes_book.asks[0]['price'])+float(no_book.asks[0]['price']):.3f}")
        print(f"  detector: {opp}")
        print()

asyncio.run(main())
