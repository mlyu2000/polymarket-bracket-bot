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

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        tot = yp + np
        priced += 1
        rows.append((tot, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    print(f"markets={len(markets)} priced={priced}")
    brk = [r for r in rows if r[0] < 1.0]
    print(f"BEST-ASK BRACKETS (sum<1.000): {len(brk)}")
    for t, q, yp, np, liq in brk[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")
    print("FLOOR (top 8 lowest best-ask sums):")
    for t, q, yp, np, liq in rows[:8]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"BEST-ASK NEAR-MISSES (1.000-1.005): {len(nm)}")
    for t, q, yp, np, liq in nm[:5]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")

asyncio.run(scan())
