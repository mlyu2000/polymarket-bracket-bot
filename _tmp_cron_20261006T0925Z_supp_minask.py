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
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    elapsed = time.time() - t0

    rows = []
    priced = 0
    brackets = []
    for m, (yb, nb) in zip(markets, books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        priced += 1
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        s = ya + na
        rows.append((s, m.question[:60], ya, na, m.liquidity))
        opp = detector.detect(m, yb, nb)
        if opp is not None:
            brackets.append((opp.total_cost, opp.net_edge, m.question[:60]))

    rows.sort()
    print(f"MIN-ASK FLOOR SCAN: {len(markets)} markets, {priced} priced, {elapsed:.1f}s")
    print(f"DETECTOR BRACKETS: {len(brackets)}")
    for b in brackets:
        print(f"  🔴 sum={b[0]:.4f} edge={b[1]:.4f} | {b[2]}")
    n_below = sum(1 for r in rows if r[0] < 1.0)
    n_1005 = sum(1 for r in rows if r[0] <= 1.005)
    print(f"best-sum<1.00: {n_below} | best-sum<=1.005: {n_1005}")
    print("TOP-10 BEST (min-ask sum):")
    for s, q, ya, na, liq in rows[:10]:
        print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
