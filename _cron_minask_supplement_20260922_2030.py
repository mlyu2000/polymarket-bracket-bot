# Supplement: min-ask near-miss analysis (asks are DESC-sorted; asks[0] is worst)
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
    el = time.time() - t0

    opps = []
    near = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append(opp)
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = yp + np_
            priced += 1
            if tot <= 1.005:
                near.append((tot, m.question[:60], yp, np_, m.liquidity,
                             int(float(min(yb.asks, key=lambda a: float(a['price']))['size'])),
                             int(float(min(nb.asks, key=lambda a: float(a['price']))['size']))))
    near.sort()
    print(f"[min-ask supplement] {len(markets)} markets, {priced} with two-sided books, in {el:.1f}s")
    print(f"detector brackets: {len(opps)}")
    print(f"min-ask near-misses (<=1.005): {len(near)}")
    for tot, q, yp, np_, liq, ys, ns in near[:10]:
        print(f"  {tot:.4f} | Yes@{yp:.3f}(sz{ys}) No@{np_:.3f}(sz{ns}) | liq={liq} | {q}")
    if near:
        print(f"true floor: {near[0][0]:.4f}")

asyncio.run(scan())
