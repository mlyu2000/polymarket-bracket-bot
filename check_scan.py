import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

Config.validate()
api = PolymarketAPI()
detector = BracketDetector()

async def run():
    markets = await api.fetch_active_markets(limit=200)
    print(f"markets fetched: {len(markets)}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    start = time.time()
    all_books = await api.fetch_order_books_batch(token_pairs, batch_size=10)
    print(f"books fetched in {time.time()-start:.1f}s, count {len(all_books)}")
    for i,(m, (yes_book,no_book)) in enumerate(zip(markets, all_books)):
        if not yes_book or not no_book: continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            print(f"BRACKET found at {i}: {m.question[:60]} sum={opp.total_cost}")
            return
        # check near
        if yes_book.asks and no_book.asks:
            yes_price = float(min(yes_book.asks, key=lambda a: float(a["price"]))["price"])
            no_price = float(min(no_book.asks, key=lambda a: float(a["price"]))["price"])
            total = yes_price + no_price
            if total <= 1.005:
                print(f"Near {total:.4f} at {i}: {m.question[:60]}")
                # continue to find brackets
    print("no brackets in first 200")

asyncio.run(run())
