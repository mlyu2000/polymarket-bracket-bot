import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
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
        tot = yp + np_
        priced += 1
        rows.append((tot, m.question[:55], yp, np_, m.liquidity))

    rows.sort()
    print(f"[supp best-ask] {priced}/{len(markets)} priced markets in {dt:.1f}s")
    print(f"min sum={rows[0][0]:.4f}" if rows else "no priced rows")
    print(f"count sum<1.000: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"count sum<=1.001: {sum(1 for r in rows if r[0] <= 1.001)}")
    print(f"count sum<=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    print("top closest (best-ask sums):")
    for tot, q, yp, np_, liq in rows[:8]:
        print(f"  {tot:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
