# Supplementary: near-misses recomputed with MIN ask (asks[0] is DESC-worst per API ordering)
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
    lt1 = []
    det_opps = 0
    no_asks = 0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            det_opps += 1
        if not yb or not nb or not yb.asks or not nb.asks:
            no_asks += 1
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        tot = yp + np_
        if tot < 1.0:
            lt1.append((tot, m.question[:55], yp, np_, m.liquidity))
        elif tot <= 1.005:
            near.append((tot, m.question[:55], yp, np_, m.liquidity))
    near.sort()
    lt1.sort()
    print(f"markets={len(markets)} no_asks_sides={no_asks}")
    print(f"BRACKETS (min-ask sum<1): {len(lt1)}")
    for t, q, yp, np_, liq in lt1[:5]:
        print(f"  🔴 [{t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}]")
    print(f"Near-misses (min-ask sum<=1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:5]:
        print(f"  [{t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}]")
    floor = min((yp+np_ for m,(yb,nb) in zip(markets, all_books) if yb and nb and yb.asks and nb.asks for yp in [min(float(a['price']) for a in yb.asks)] for np_ in [min(float(a['price']) for a in nb.asks)]), default=None)
    print(f"min best-ask sum (floor): {floor:.4f}" if floor else "floor: n/a")
    print(f"detector-reported brackets: {det_opps}")

asyncio.run(scan())
