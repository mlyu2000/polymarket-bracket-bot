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
    scan_time = time.time() - t0

    opps = []
    near = []
    floor = (9.0, None)
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            tot = yp + np_
            if tot < floor[0]:
                floor = (tot, m.question[:60])
            if tot <= 1.005:
                near.append((tot, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    return markets, opps, near, floor, scan_time

markets, opps, near, floor, scan_time = asyncio.run(scan())
print(f"SUPP min-ask scan: {len(markets)} markets in {scan_time:.1f}s")
print(f"BRACKETS(min-ask sum<gate): {len(opps)}")
for s, e, sh, q in sorted(opps):
    print(f"  sum={s:.4f} edge={e:.4f} shares={sh} | {q}")
print(f"Near-misses (min-ask sum<=1.005): {len(near)}")
for tot, q, yp, np_, liq in near[:10]:
    print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"Global floor: sum={floor[0]:.4f} | {floor[1]}")
