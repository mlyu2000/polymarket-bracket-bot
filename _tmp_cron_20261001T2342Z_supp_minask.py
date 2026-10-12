import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    # Correct best-ask analysis: CLOB asks are DESC-sorted, use min().
    near_misses = []
    brackets_true = []
    floors = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        total = yp + np_
        floors.append((total, m.question[:50], m.liquidity))
        if total < 1.0:
            brackets_true.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            near_misses.append((total, m.question[:50], yp, np_, m.liquidity))

    near_misses.sort()
    brackets_true.sort()
    floors.sort()
    priced = len(floors)
    print(f"⏱ Supplemental min-ask scan: {len(markets)} markets in {scan_time:.1f}s ({priced} priced)")
    print(f"🔴 TRUE brackets (min-ask sum < 1.00): {len(brackets_true)}")
    for t, q, yp, np_, liq in brackets_true[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"📊 Corrected near-misses (1.00 < sum <= 1.005): {len(near_misses)}")
    for t, q, yp, np_, liq in near_misses[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"📉 Global floor (top 5 lowest sums across all priced markets):")
    for t, q, liq in floors[:5]:
        print(f"  {t:.4f} | liq={liq} | {q}")

asyncio.run(scan())
