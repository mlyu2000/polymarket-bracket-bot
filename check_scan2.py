import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

Config.validate()
api = PolymarketAPI()
detector = BracketDetector()

async def run():
    markets = await api.fetch_active_markets(limit=500)
    print(f"markets fetched: {len(markets)}")
    # Filter to ensure binary and liquidity
    markets = [m for m in markets if m.liquidity >= Config.MIN_LIQUIDITY_USDC]
    print(f"after liquidity filter: {len(markets)}")
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    start = time.time()
    all_books = await api.fetch_order_books_batch(token_pairs, batch_size=20)
    print(f"books fetched in {time.time()-start:.1f}s")
    opps = []
    near = []
    for m, (yes_book,no_book) in zip(markets, all_books):
        if not yes_book or not no_book: continue
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((m.question, opp.total_cost, opp.net_edge))
            print(f"BRACKET: {opp.total_cost:.4f} {m.question[:80]}")
        if yes_book.asks and no_book.asks:
            yes_price = float(min(yes_book.asks, key=lambda a: float(a["price"]))["price"])
            no_price = float(min(no_book.asks, key=lambda a: float(a["price"]))["price"])
            total = yes_price + no_price
            if total <= 1.005 and total >= 1.0:
                near.append((total, m.question))
    print(f"Total brackets: {len(opps)}")
    print(f"Total near-misses (1.0-1.005): {len(near)}")
    for t,q in near[:20]:
        print(f"  {t:.4f} {q[:80]}")

asyncio.run(run())
