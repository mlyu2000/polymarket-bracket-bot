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
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    print(f"min-ask scan: {len(markets)} markets, {len(rows)} priced pairs in {dt:.1f}s")
    under = [r for r in rows if r[0] < 1.0]
    print(f"true brackets (sum<1.00): {len(under)}")
    for total, q, yp, np_, liq in under:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses (sum<=1.005): {len(nm)}")
    for total, q, yp, np_, liq in nm[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if rows:
        print(f"best (lowest) sums overall: " + ", ".join(f"{r[0]:.4f}" for r in rows[:5]))

asyncio.run(scan())
