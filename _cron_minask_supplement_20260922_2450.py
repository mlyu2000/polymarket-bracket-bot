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
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))

    rows.sort()
    print(f"priced markets (both sides have asks): {priced}")
    print("--- true floor: best-ask (min) sums, bottom 8 ---")
    for total, q, ya, na, liq in rows[:8]:
        print(f"  {total:.3f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    under = [r for r in rows if r[0] < 1.0]
    print(f"minask sum<1.00 count: {len(under)}")
    for total, q, ya, na, liq in under:
        print(f"  SUB-1 {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"minask near-miss [1.000,1.005] count: {len(nm)}")
    for total, q, ya, na, liq in nm[:5]:
        print(f"  NM {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(scan())
