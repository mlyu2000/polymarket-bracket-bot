import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    opps = []
    for m in markets:
        if m.liquidity < Config.MIN_LIQUIDITY_USDC:
            continue
        if not m.active or m.closed:
            continue
        token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1])]
        books = await api.fetch_order_books_batch(token_pairs)
        yes_book, no_book = books[0]
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        # detector uses min price
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append(opp)
            print(f"Bracket found: {opp.total_cost:.4f} {m.question[:60]}")
    print(f"Total brackets: {len(opps)}")

asyncio.run(test())
