"""Supplement: near-miss floor using BEST ask (min price).
CLOB /book asks are DESC-sorted, so asks[0] is the WORST ask (~0.999).
detector.py itself uses min() — this pass aligns the near-miss report with it."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    floor = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            tot = yp + np_
            priced += 1
            opp = detector.detect(m, yes_book, no_book)
            if opp is None and tot <= 1.005:
                floor.append((tot, m.question[:50], yp, np_, m.liquidity))
    floor.sort()
    return len(markets), priced, floor

markets_n, priced_n, floor = asyncio.run(scan())
print(f"Best-ask floor supplement: {len(floor)} near-misses (<=1.005) across {priced_n}/{markets_n} priced markets")
for tot, q, yp, np_, liq in floor[:10]:
    print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
