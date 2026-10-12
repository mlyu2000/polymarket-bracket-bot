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
    scan_time = time.time() - t0

    opps, near, priced = [], [], 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        total = yp + np_
        priced += 1
        if total < 1.0:
            opp = detector.detect(m, yb, nb)
            opps.append((total, m.question[:60], yp, np_, m.liquidity, opp))
        elif total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    opps.sort()
    return markets, opps, near, priced, scan_time

markets, opps, near, priced, st = asyncio.run(scan())
print(f"[min-ask supplement] {len(markets)} markets, {priced} with both books, {st:.1f}s")
print(f"TRUE BRACKETS (best-ask sum < 1.00): {len(opps)}")
for total, q, yp, np_, liq, opp in opps:
    det = "DETECTED" if opp else "detector-skipped"
    extra = f" edge={opp.net_edge:.4f} shares={opp.max_shares}" if opp else ""
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {det}{extra} | {q}")
print(f"NEAR-MISSES (1.00 < sum <= 1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
