import asyncio
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def test():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    for m, (yes_book, no_book) in zip(markets, all_books):
        if "Michelle Bolsonaro" in m.question:
            print("Market found")
            print(f"active={m.active}, closed={m.closed}, liquidity={m.liquidity}")
            print(f"yes_book exists={yes_book is not None}, no_book exists={no_book is not None}")
            if yes_book:
                print(f"yes_asks count={len(yes_book.asks)}")
            if no_book:
                print(f"no_asks count={len(no_book.asks)}")
            opp = detector.detect(m, yes_book, no_book)
            print(f"Detector result: {opp}")
            if opp:
                print(f"opp.yes_price={opp.yes_price}, opp.no_price={opp.no_price}")
            break

asyncio.run(test())
