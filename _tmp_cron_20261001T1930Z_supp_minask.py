import asyncio, logging, time
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

    # Corrected near-miss: use BEST (min) ask, since CLOB asks are DESC-sorted
    corrected = []
    brackets_min = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        if total < 1.0:
            brackets_min.append((total, m.question[:60], yp, np, m.liquidity))
        elif total <= 1.005:
            corrected.append((total, m.question[:50], yp, np, m.liquidity))
    corrected.sort()
    brackets_min.sort()
    return markets, brackets_min, corrected

markets, brackets_min, corrected = asyncio.run(scan())
print(f"[min-ask check] markets={len(markets)}")
print(f"[min-ask check] true brackets (min-ask sum<1): {len(brackets_min)}")
for t, q, yp, np, liq in brackets_min[:10]:
    print(f"  🔴 {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"[min-ask check] near-misses (min-ask sum<=1.005): {len(corrected)}")
for t, q, yp, np, liq in corrected[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
