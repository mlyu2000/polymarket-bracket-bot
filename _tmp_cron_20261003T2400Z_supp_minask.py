"""Supplement: best-ask (min price) totals — CLOB returns asks DESC-sorted,
so asks[0] in the verbatim prompt block is the WORST ask (~0.999) and
near-misses under-report. detector.detect() itself uses min() correctly."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    true_brackets = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        t = ya + na
        if t < 1.0:
            true_brackets.append((t, m.question[:60], ya, na, m.liquidity))
        rows.append((t, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    true_brackets.sort()
    print(f"Markets fetched: {len(markets)} | priced (both-side asks): {priced}")
    print(f"TRUE brackets on best asks (sum<1.00): {len(true_brackets)}")
    for t, q, ya, na, liq in true_brackets[:10]:
        print(f"  🔴 {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print("Top-10 lowest best-ask totals:")
    for t, q, ya, na, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"Near-miss count best-ask (<=1.005): {sum(1 for r in rows if r[0] <= 1.005)}")

asyncio.run(supp())
