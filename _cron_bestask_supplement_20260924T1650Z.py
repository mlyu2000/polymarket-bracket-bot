# Supplement: near-miss using BEST asks (min of asks list), since /book asks are DESC-sorted.
# detector.py already uses min(); this corrects the cron prompt's asks[0] near-miss block.
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
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    opps = []
    near = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append(opp)
        if yb and nb and yb.asks and nb.asks:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = yp + np_
            if tot <= 1.005:
                near.append((tot, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    print(f"[best-ask supplement] {len(markets)} markets, {priced} priced in {dt:.1f}s")
    print(f"detector brackets: {len(opps)}")
    print(f"best-ask near-misses (<=1.005): {len(near)}")
    for tot, q, yp, np_, liq in near[:10]:
        print(f"  {tot:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
