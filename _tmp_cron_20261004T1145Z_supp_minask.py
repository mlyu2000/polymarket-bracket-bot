import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    opps = []
    priced = 0
    floor = None
    floor_q = None
    floor_liq = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if floor is None or total < floor:
                floor, floor_q, floor_liq = total, m.question[:60], m.liquidity
            if total <= 1.005:
                near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    opps.sort()
    print(f"priced_markets={priced} total_markets={len(markets)}")
    print(f"detector_opps={len(opps)}")
    for s, e, sh, q in opps[:5]:
        print(f"  OPP sum={s:.3f} edge={e:.4f} shares={sh} | {q}")
    print(f"best_ask_near_misses(<=1.005)={len(near)}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"floor_sum={floor:.4f} | liq={floor_liq} | {floor_q}")
    counts = {'<=1.010': 0}
    async def _c():
        pass
    # count sum<=1.010
    c1010 = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            t = min(float(a['price']) for a in yb.asks) + min(float(a['price']) for a in nb.asks)
            if t <= 1.010:
                c1010 += 1
    print(f"count_sum<=1.010={c1010}")

asyncio.run(scan())
