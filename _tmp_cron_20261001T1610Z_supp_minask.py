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
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    detected = 0
    priced = 0
    floor = 9.9
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            detected += 1
            continue
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = yp + np_
            priced += 1
            floor = min(floor, total)
            if total <= 1.01:
                near.append((total, m.question[:60], yp, np_, m.liquidity, m.active, m.closed))
    near.sort()
    print(f"markets={len(markets)} priced_pairs={priced} detector_hits={detected} true_floor={floor:.4f}")
    print(f"TRUE near-misses (min-ask sum<=1.01): {len(near)}")
    for row in near[:10]:
        total, q, yp, np_, liq, act, cls = row
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} active={act} closed={cls} | {q}")

asyncio.run(scan())
