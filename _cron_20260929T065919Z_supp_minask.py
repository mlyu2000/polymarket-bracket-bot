# Supplement: true floor using BEST (min) asks. CLOB /book asks are DESC-sorted,
# so asks[0] in the verbatim script is the WORST ask (~0.999) -> near-miss list there is bogus.
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    n_detector = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            n_detector += 1
        if yes_book and no_book and yes_book.asks and no_book.asks:
            y = min(float(a['price']) for a in yes_book.asks)
            n = min(float(a['price']) for a in no_book.asks)
            rows.append((y + n, m.question[:60], y, n, m.liquidity))
    rows.sort()
    return rows, n_detector, len(markets)

rows, n_detector, nmarkets = asyncio.run(scan())
print(f"markets={nmarkets} detector_brackets={n_detector}")
print("TOP 10 BY BEST-ASK SUM:")
for total, q, y, n, liq in rows[:10]:
    print(f"  {total:.3f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
print(f"best-ask sums < 1.00: {sum(1 for r in rows if r[0] < 1.0)} | <= 1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
