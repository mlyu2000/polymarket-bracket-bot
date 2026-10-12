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
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    bracket_like = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        y_min = min(float(a['price']) for a in yb.asks)
        n_min = min(float(a['price']) for a in nb.asks)
        y_a0 = float(yb.asks[0]['price'])
        n_a0 = float(nb.asks[0]['price'])
        total = y_min + n_min
        rows.append((total, m.question[:55], y_min, n_min, m.liquidity))
        opp = detector.detect(m, yb, nb)
        if opp:
            bracket_like += 1
    rows.sort()
    print(f"detector-flagged brackets (best-ask): {bracket_like}")
    print(f"markets with books: {len(rows)}")
    print("FLOOR (true min-ask sums, lowest 10):")
    for total, q, y, n, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    near = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses by MIN-ASK (<=1.005): {len(near)}")
    under = [r for r in rows if r[0] < 1.0]
    print(f"sum<1.00 by MIN-ASK: {len(under)}")
    for total, q, y, n, liq in under[:10]:
        print(f"  [MIN-ASK<1] {total:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

asyncio.run(supp())
