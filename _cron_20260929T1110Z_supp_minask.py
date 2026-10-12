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
    books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        tot = ya + na
        priced += 1
        opp = detector.detect(m, yb, nb)
        rows.append((tot, m.question[:60], ya, na, m.liquidity, opp is not None))
    rows.sort()
    print(f"priced markets: {priced}")
    print("best-ask floor (5 lowest sums):")
    for tot, q, ya, na, liq, detected in rows[:5]:
        print(f"  {tot:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | det={detected} | {q}")
    under = [r for r in rows if r[0] < 1.0]
    print(f"true sub-1.00 sums (best-ask): {len(under)}")
    for r in under:
        print(f"  {r[0]:.3f} | {r[1]}")

asyncio.run(scan())
