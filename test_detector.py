import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=100)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    count = 0
    for m, (yes_book, no_book) in zip(markets, books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            count += 1
            print(f"FOUND: {m.question[:60]} sum={opp.total_cost:.4f} edge={opp.net_edge:.4f}")
    print(f"Total brackets: {count}")

asyncio.run(test())
