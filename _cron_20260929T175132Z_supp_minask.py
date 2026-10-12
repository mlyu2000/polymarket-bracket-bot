import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near = []
    priced = 0
    best_floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        if best_floor is None or total < best_floor[0]:
            best_floor = (total, m.question[:50], ya, na, m.liquidity)
        if total < 1.0:
            opps.append((total, m.question[:60], ya, na, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:50], ya, na, m.liquidity))

    opps.sort()
    near.sort()
    print(f"[min-ask supplement] {priced}/{len(markets)} markets priced in {scan_time:.1f}s")
    print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(opps)}")
    for total, q, ya, na, liq in opps[:10]:
        print(f"  >> {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    print(f"Near-misses (min-ask sum <=1.005): {len(near)}")
    for total, q, ya, na, liq in near[:5]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    if best_floor:
        print(f"Best floor: {best_floor[0]:.4f} | Yes@{best_floor[2]:.3f} No@{best_floor[3]:.3f} | liq={best_floor[4]} | {best_floor[1]}")

asyncio.run(scan())
