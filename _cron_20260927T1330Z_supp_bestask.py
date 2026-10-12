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
    scan_time = time.time() - t0

    sums = []
    brackets = []
    near = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(float(a['price']) for a in yes_book.asks)
        na = min(float(a['price']) for a in no_book.asks)
        total = ya + na
        sums.append(total)
        if total < 1.0:
            brackets.append((total, m.question[:60], ya, na, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:50], ya, na, m.liquidity))
    brackets.sort()
    near.sort()
    return len(markets), scan_time, len(sums), (min(sums) if sums else None), brackets, near

n, t, priced, floor, brackets, near = asyncio.run(scan())
print(f"Best-ask supplement: {n} markets in {t:.1f}s | priced pairs={priced} | floor sum={floor}")
print(f"TRUE BRACKETS (best-ask sum<1.00): {len(brackets)}")
for s, q, ya, na, liq in brackets[:10]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
print(f"Near-misses <=1.005 (best-ask): {len(near)}")
for s, q, ya, na, liq in near[:8]:
    print(f"  {s:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
