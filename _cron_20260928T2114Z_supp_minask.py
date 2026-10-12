import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    # Best-ask (min over levels) near-misses — CLOB asks are DESC-sorted,
    # so asks[0] is the WORST ask. This complements the verbatim cron scan.
    rows = []
    brk = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        total = yp + np
        if total < 1.0:
            brk.append((total, m.question[:60], yp, np, m.liquidity))
        elif total <= 1.005:
            rows.append((total, m.question[:50], yp, np, m.liquidity))
    rows.sort(); brk.sort()
    print(f"[best-ask supplemental] {len(markets)} markets in {dt:.1f}s")
    print(f"best-ask brackets (sum<1.000): {len(brk)}")
    for t, q, yp, np, liq in brk[:10]:
        print(f"  🔴 {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"best-ask near-misses (<=1.005): {len(rows)}")
    for t, q, yp, np, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
