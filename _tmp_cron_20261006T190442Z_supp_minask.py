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

    near = []
    priced = 0
    floor = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            # best ask = min price (asks are DESC-sorted in CLOB /book)
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            priced += 1
            if floor is None or total < floor[0]:
                floor = (total, m.question[:60], yp, np_, m.liquidity)
            if total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    print(f"SUPP min-ask scan: {len(markets)} markets, {priced} priced, {scan_time:.1f}s")
    if floor:
        print(f"FLOOR: {floor[0]:.3f} | Yes@{floor[2]:.3f} No@{floor[3]:.3f} | liq={floor[4]} | {floor[1]}")
    print(f"MINASK near-misses (<=1.005): {len(near)}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
