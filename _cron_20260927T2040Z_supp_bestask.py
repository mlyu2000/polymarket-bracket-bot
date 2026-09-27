import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    priced = 0
    near = []
    floor = None
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = yp + np_
            if floor is None or total < floor[0]:
                floor = (total, m.question[:50], yp, np_, m.liquidity)
            if total <= 1.005:
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    print(f"priced markets (best-ask): {priced}")
    if floor:
        print(f"floor: {floor[0]:.3f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | liq={floor[4]} | {floor[1]}")
    print(f"best-ask near-misses (<=1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:8]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(supp())
