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
    dt = time.time() - t0
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    print(f"[min-ask supplement] {len(markets)} markets, {priced} priced, {dt:.1f}s")
    brk = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"true-brackets(min-ask sum<1.00): {len(brk)}")
    for t, q, yp, np_, liq in brk[:10]:
        print(f"  {t:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}")
    print(f"near-misses(1.000-1.005): {len(nm)}")
    for t, q, yp, np_, liq in nm[:5]:
        print(f"  {t:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}")
    if rows:
        t, q, yp, np_, liq = rows[0]
        print(f"best sum overall: {t:.4f} | {q}")

asyncio.run(scan())
