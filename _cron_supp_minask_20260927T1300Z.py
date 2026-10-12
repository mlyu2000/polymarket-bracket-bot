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
    brk = 0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            brk += 1
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    return brk, rows, dt

brk, rows, dt = asyncio.run(scan())
print(f"[supplement: min-ask] {len(rows)} priced markets in {dt:.1f}s; detector brackets={brk}")
print("Cheapest true YES+NO sums:")
for s, q, yp, np, liq in rows[:8]:
    print(f"  {s:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
print(f"count sum<=1.01: {sum(1 for r in rows if r[0] <= 1.01)}")
