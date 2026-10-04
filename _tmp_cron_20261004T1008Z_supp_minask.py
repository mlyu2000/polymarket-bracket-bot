import asyncio, logging, time
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
    mins = []
    floor = None
    br = 0
    for m, (yb, nb) in zip(markets, books):
        opp = detector.detect(m, yb, nb)
        if opp:
            br += 1
            continue
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            t = ya + na
            mins.append((t, m.question[:55], ya, na, m.liquidity))
            if floor is None or t < floor[0]:
                floor = (t, m.question[:55], ya, na, m.liquidity)
    mins.sort()
    print(f"both-sides-priced: {priced}/{len(markets)}")
    print(f"detector brackets (min-ask): {br}")
    if floor:
        print(f"floor sum: {floor[0]:.3f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | liq={floor[4]} | {floor[1]}")
    print("min-ask near-misses <=1.005:")
    nm = [x for x in mins if x[0] <= 1.005]
    print(f"  count={len(nm)}")
    for t, q, ya, na, liq in nm[:10]:
        print(f"  {t:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(supp())
