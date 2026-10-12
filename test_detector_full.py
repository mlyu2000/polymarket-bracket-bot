import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    brackets = []
    for m in markets:
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append(opp)
    print(f"Brackets detected: {len(brackets)}")
    for opp in brackets[:10]:
        print(f"{opp.total_cost:.4f} {opp.yes_price:.3f} {opp.no_price:.3f} {opp.market.question[:60]}")

asyncio.run(test())
