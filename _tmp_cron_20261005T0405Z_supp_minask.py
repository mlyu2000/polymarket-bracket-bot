import asyncio, logging, time, json
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
    scan_time = time.time() - t0

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        rows.append((ya + na, ya, na, m.question[:70], m.liquidity))
    rows.sort()
    return rows, len(markets), scan_time

rows, n, t = asyncio.run(scan())
print(f"min-ask pass: {n} markets in {t:.1f}s; {len(rows)} priced")
print(f"true floor sum: {rows[0][0]:.4f}" if rows else "no priced rows")
lm = [r for r in rows if r[0] <= 1.005]
print(f"min-ask near-misses (<=1.005): {len(lm)}")
for s, ya, na, q, liq in lm[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
br = [r for r in rows if r[0] < 1.0]
print(f"min-ask BRACKETS (sum<1.0): {len(br)}")
for s, ya, na, q, liq in br[:10]:
    print(f"  [!] {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
