import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    best = []   # true best-ask sums (min over asks)
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            continue
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_bids = [float(a['price']) for a in yes_book.asks]
        no_bids = [float(a['price']) for a in no_book.asks]
        ya, na = min(yes_bids), min(no_bids)
        total = ya + na
        if total <= 1.005:
            best.append((round(total, 4), m.question[:50], ya, na, m.liquidity))
    best.sort()
    print(f"SUPP best-ask near-misses (≤1.005, excl. detector brackets): {len(best)}")
    for t, q, ya, na, liq in best[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(supp())
