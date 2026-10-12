import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # asks are DESC-sorted by API; best ask = min price
        ya = [float(a['price']) for a in yes_book.asks]
        na = [float(a['price']) for a in no_book.asks]
        best_yes = min(ya)
        best_no = min(na)
        total = best_yes + best_no
        priced += 1
        rows.append((total, m.question[:55], best_yes, best_no, m.liquidity))

    rows.sort()
    print(f"Priced markets (min-ask basis): {priced}")
    brackets = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for t, q, y, n, liq in brackets[:10]:
        print(f"  🔴 {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    print(f"Near-misses (min-ask sum 1.000-1.005): {len(nm)}")
    for t, q, y, n, liq in nm[:10]:
        print(f"  🟡 {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
    print("Top 5 lowest sums overall:")
    for t, q, y, n, liq in rows[:5]:
        print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | {q}")

asyncio.run(scan())
