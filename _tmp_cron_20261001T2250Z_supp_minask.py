import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    # Also recompute the "verbatim" near-miss using asks[0] to confirm
    # the DESC-sort artifact yields nothing.
    verbatim_nm = 0
    best_nm = []
    checked = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        checked += 1
        a0 = float(yb.asks[0]['price']) + float(nb.asks[0]['price'])
        if a0 <= 1.005:
            verbatim_nm += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        total = yp + np_
        if total <= 1.005:
            best_nm.append((round(total, 4), m.question[:60], yp, np_, m.liquidity))
    best_nm.sort()
    print(f"markets={len(markets)} books_checked={checked}")
    print(f"verbatim_asks0_near_misses={verbatim_nm}")
    print(f"TRUE best-ask near-misses (sum<=1.005): {len(best_nm)}")
    for t, q, yp, np_, liq in best_nm[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    floors = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        floors.append((round(yp+np_,4), m.question[:50]))
    floors.sort()
    print("GLOBAL FLOOR (10 lowest sums):")
    for t, q in floors[:10]:
        print(f"  {t:.4f} | {q}")

asyncio.run(main())
