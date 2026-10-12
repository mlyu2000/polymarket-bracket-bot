import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        rows.append((total, m.question[:55], yp, np_, m.liquidity))

    rows.sort()
    print(f"[corrected best-ask scan] {priced}/{len(markets)} priced in {dt:.1f}s")
    print("--- TRUE FLOOR (min best-ask sums) ---")
    for total, q, yp, np_, liq in rows[:10]:
        flag = " <1.00 BRACKET!" if total < 1.0 else (" <=1.005 near" if total <= 1.005 else "")
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:,.0f} | {q}{flag}")
    n_lt1  = sum(1 for r in rows if r[0] < 1.0)
    n_1005 = sum(1 for r in rows if r[0] <= 1.005)
    n_101  = sum(1 for r in rows if r[0] <= 1.01)
    print(f"SUMMARY: sum<1.00: {n_lt1} | sum<=1.005: {n_1005} | sum<=1.01: {n_101}")

asyncio.run(scan())
