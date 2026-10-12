"""Supplement: correct near-miss floor using min-ask (best ask by price),
because the CLOB payload lists asks DESC-sorted — asks[0] is the worst ask.
Also reports true min-sum across all priced markets and executes any
detector-findings via paper executor already done in main scan."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        priced += 1
        rows.append((y + n, y, n, m.question[:55], m.liquidity))
    rows.sort()
    print(f"min-ask scan: {len(markets)} markets, {priced} priced, {dt:.1f}s")
    print(f"floor (min sum): {rows[0][0]:.4f}" if rows else "no priced rows")
    print("top min-ask near-misses (<=1.005):")
    cnt = 0
    for total, y, n, q, liq in rows:
        if total <= 1.005:
            cnt += 1
            if cnt <= 10:
                print(f"  {total:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    print(f"total min-ask near-misses: {cnt}")

asyncio.run(scan())
