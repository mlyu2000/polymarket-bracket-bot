"""Supplement: correct near-miss calc using best ask (min price), since
CLOB /book asks are DESC-sorted and asks[0] is the WORST ask (see memory).
Detection itself (detector.py) already uses min()."""
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
    el = time.time() - t0

    opps, near = [], []
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
    print(f"corrected scan: {len(markets)} markets ({priced} priced) in {el:.1f}s")
    print(f"BRACKETS via detector: {len(opps)}")
    for o in opps:
        print(f"  {o.total_cost:.3f} edge={o.net_edge:.4f} Yes@{o.yes_price:.3f} No@{o.no_price:.3f} shares={o.max_shares}")
    print(f"NEAR-MISSES best-ask sum<=1.005: {len(near)}")
    for tot, q, yp, np_, liq in near[:10]:
        print(f"  {tot:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
