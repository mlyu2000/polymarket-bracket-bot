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
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        priced += 1
        rows.append((total, m.question[:60], ya, na, m.liquidity))

    rows.sort()
    print(f"supp best-ask scan: {priced}/{len(markets)} priced in {dt:.1f}s")
    brk = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"true brackets (<1.000): {len(brk)}")
    for r in brk:
        print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    print(f"near-misses (1.000-1.005): {len(nm)}")
    for r in nm[:10]:
        print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    print("top-5 lowest true totals:")
    for r in rows[:5]:
        print(f"  {r[0]:.3f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")

asyncio.run(scan())
