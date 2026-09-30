# Supplement: near-miss check using BEST ask (min price) instead of asks[0].
# Polymarket CLOB /book returns asks DESC-sorted, so asks[0] is the worst ask
# (~0.999) and the verbatim near-miss block structurally reports 0.
import asyncio, logging, time, json
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

    near_misses = []
    brackets = []
    floor = None
    floor_q = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yes_price = min(float(a['price']) for a in yes_book.asks)
        no_price = min(float(a['price']) for a in no_book.asks)
        total = yes_price + no_price
        if floor is None or total < floor:
            floor, floor_q = total, m.question[:60]
        if total < 1.0:
            brackets.append((total, m.question[:60], yes_price, no_price, m.liquidity))
        elif total <= 1.005:
            near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    brackets.sort()
    out = {
        'markets': len(markets),
        'scan_time': scan_time,
        'floor': floor,
        'floor_market': floor_q,
        'brackets_min_ask': brackets,
        'near_misses_min_ask': near_misses,
    }
    print(f"best-ask supplement: {len(markets)} markets in {scan_time:.1f}s")
    print(f"MIN floor sum: {floor:.3f} ({floor_q})")
    print(f"BRACKETS (min-ask, sum<1.00): {len(brackets)}")
    for total, q, yp, np, liq in brackets:
        print(f"  🔴 {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"Near-misses (min-ask, <=1.005): {len(near_misses)}")
    for total, q, yp, np, liq in near_misses[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
    with open('runs/scan_20260928T1940Z_floor.json', 'w') as f:
        json.dump(out, f, indent=2, default=str)

asyncio.run(scan())
