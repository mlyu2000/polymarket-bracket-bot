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
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    print(f"min-ask check: {len(markets)} markets in {dt:.1f}s; priced={len(rows)}")
    brackets = [r for r in rows if r[0] < 1.0]
    near = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"TRUE brackets (min-ask sum<1.00): {len(brackets)}")
    for t, q, yp, np_, liq in brackets[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"Near-misses (1.000-1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:5]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if rows:
        print(f"Floor sum observed: {rows[0][0]:.4f}")

asyncio.run(scan())
