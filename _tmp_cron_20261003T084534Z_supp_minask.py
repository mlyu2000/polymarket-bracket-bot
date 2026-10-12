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
        rows.append((total, m.question[:55], ya, na, m.liquidity))
    rows.sort()
    print(f"Supp (best-ask/min): {priced}/{len(markets)} priced markets in {dt:.1f}s")
    print("--- Top 10 lowest YES+NO best-ask sums ---")
    for total, q, ya, na, liq in rows[:10]:
        flag = "BRACKET" if total < 1.0 else ("near" if total <= 1.005 else "")
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {flag} | {q}")
    lt1 = [r for r in rows if r[0] < 1.0]
    le1005 = [r for r in rows if r[0] <= 1.005]
    print(f"Sum < 1.00: {len(lt1)} | Sum <= 1.005: {len(le1005)} | Floor: {rows[0][0]:.4f}" if rows else "no priced markets")

asyncio.run(scan())
