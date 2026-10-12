# Supplementary: corrected near-miss computation using best ask = min(asks)
# (asks[0] in CLOB payload is the WORST ask, desc-sorted; see memory note)
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if not m.active or m.closed or m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        if total <= 1.005:
            near.append((total, m.question[:50], yp, np, m.liquidity))
    near.sort()
    print(f"⏱ corr. scan {dt:.1}s")
    print(f"📊 NEAR-MISSES (best-ask min(), sum<=1.005): {len(near)}")
    for total, q, yp, np, liq in near[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
    return near

asyncio.run(scan())
