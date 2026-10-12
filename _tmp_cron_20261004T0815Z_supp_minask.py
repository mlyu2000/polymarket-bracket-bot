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
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        priced += 1
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity, m.active, m.closed))
    rows.sort()
    print(f"min-ask floor scan: {len(markets)} markets, {priced} priced, {el:.1f}s")
    print("TOP-10 lowest YES+NO (min ask):")
    for total, q, yp, np, liq, act, cls in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    lt1 = [r for r in rows if r[0] < 1.0]
    le1005 = [r for r in rows if r[0] <= 1.005]
    print(f"sum<1.000: {len(lt1)}  sum<=1.005: {len(le1005)}")
    # detector-passed brackets among low sums that failed only due to guards
    for total, q, yp, np, liq, act, cls in rows[:5]:
        opp = None
        for m,(yb,nb) in zip(markets, all_books):
            if m.question[:60] == q:
                opp = detector.detect(m, yb, nb)
                break
        print(f"  detector({total:.4f}) -> {'OPP edge='+format(opp.net_edge,'.4f') if opp else 'None (guards/no edge)'}")

asyncio.run(scan())
