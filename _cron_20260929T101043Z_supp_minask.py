# Corrected near-miss sweep: uses MIN ask (asks list is DESC-sorted; asks[0] is worst ask)
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
    opps, near = [], []
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append(opp)
        elif yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = yp + np_
            if total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    print(f"⏱ corrected sweep: {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ DETECTOR BRACKETS (min-ask, sum<1.00): {len(opps)}")
    for o in opps:
        print(f"  🔴 sum={o.total_cost:.4f} edge={o.net_edge:.4f} Yes@{o.yes_price:.3f} No@{o.no_price:.3f} shares={o.max_shares} liq={o.market.liquidity if hasattr(o,'market') else '?'} | {o.market.question[:60] if hasattr(o,'market') else ''}")
    print(f"📊 NEAR-MISSES ≤1.005 (corrected min-ask): {len(near)}")
    for t, q, yp, np_, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if near:
        print(f"BEST FLOOR: {min(n[0] for n in near):.4f}")

asyncio.run(scan())
