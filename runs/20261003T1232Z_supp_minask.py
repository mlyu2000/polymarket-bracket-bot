import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    bestask_near = []
    priced_both = 0
    floor = 9.9
    floor_q = ''
    brackets_sum_lt1 = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        total = yp + np_
        priced_both += 1
        if total < floor:
            floor = total
            floor_q = m.question[:60]
        if total < 1.0 and m.liquidity > 0:
            brackets_sum_lt1 += 1
        if total <= 1.005:
            bestask_near.append((total, m.question[:55], yp, np_, m.liquidity))
    bestask_near.sort()
    print(f"markets={len(markets)} priced_both_sides={priced_both}")
    print(f"floor_true_best_ask={floor:.4f} ({floor_q})")
    print(f"true_brackets_sum_lt_1.00 (liq>0)={brackets_sum_lt1}")
    print(f"best_ask_near_misses_<=1.005={len(bestask_near)}")
    for t, q, yp, npp, liq in bestask_near[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{npp:.3f} | liq={liq} | {q}")

asyncio.run(scan())
