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
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yb = min(float(a['price']) for a in yes_book.asks)
        nb = min(float(a['price']) for a in no_book.asks)
        t = yb + nb
        if t <= 1.005:
            rows.append((t, yb, nb, m.liquidity, m.question[:60]))
    rows.sort()
    return len(markets), time.time() - t0, rows

n, dt, rows = asyncio.run(scan())
print(f"best-ask scan: {n} markets in {dt:.1f}s | best-ask sums <=1.005: {len(rows)}")
for t, yb, nb, liq, q in rows[:10]:
    print(f"  {t:.4f} | Yes@{yb:.3f} No@{nb:.3f} | liq={liq} | {q}")
