"""Supplementary near-miss scan using BEST asks (min price), not asks[0].
Polymarket CLOB /book lists asks DESC-sorted, so asks[0] is the worst price."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def run():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    priced = 0
    best_brackets = []
    best_near = []
    floor = None
    floor_q = ''
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        t = yp + np_
        if floor is None or t < floor:
            floor, floor_q = t, m.question[:60]
        if t < 1.00:
            best_brackets.append((t, m.question[:60], yp, np_, m.liquidity))
        elif t <= 1.005:
            best_near.append((t, m.question[:60], yp, np_, m.liquidity))
    best_brackets.sort()
    best_near.sort()
    print(f"markets={len(markets)} priced_with_asks={priced}")
    if floor is not None:
        print(f"true floor (min best-ask sum): {floor:.4f} | {floor_q}")
    else:
        print("floor: none")
    print(f"sum<1.00 on best asks (true brackets): {len(best_brackets)}")
    for t, q, yp, np_, liq in best_brackets[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"near-misses (1.000<sum<=1.005) on best asks: {len(best_near)}")
    for t, q, yp, np_, liq in best_near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(run())
