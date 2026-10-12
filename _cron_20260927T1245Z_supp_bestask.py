"""Supplementary: near-miss recheck using BEST asks (min price), correcting
the known asks[0] DESC-sort defect in the verbatim script's near-miss block."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    brackets = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        total = ya + na
        if total < 1.0:
            brackets.append((total, m.question[:60], ya, na, m.liquidity))
        elif total <= 1.005:
            rows.append((total, m.question[:50], ya, na, m.liquidity))

    rows.sort()
    brackets.sort()
    print(f"[best-ask recheck] {len(markets)} markets in {dt:.1f}s")
    print(f"TRUE brackets (best-ask sum<1.00, any liquidity): {len(brackets)}")
    for t, q, yp, np, liq in brackets[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"Near-misses best-ask (1.00<sum<=1.005): {len(rows)}")
    for t, q, yp, np, liq in rows[:5]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
