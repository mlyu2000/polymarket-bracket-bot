import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            rows.append((total, m.question[:60], yes_price, no_price, m.liquidity))
    rows.sort()
    print(f"Supp min-ask scan: {priced}/{len(markets)} priced markets in {scan_time:.1f}s")
    print("Top-12 lowest true best-ask sums:")
    for total, q, yp, np, liq in rows[:12]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    lt1 = [r for r in rows if r[0] < 1.0]
    le1005 = [r for r in rows if r[0] <= 1.005]
    print(f"True brackets (<1.000): {len(lt1)} | True near-misses (<=1.005): {len(le1005)}")
    for total, q, yp, np, liq in lt1:
        print(f"  BRACKET {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(supp())
