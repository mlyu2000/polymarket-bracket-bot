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

    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total <= 1.005:
            near.append((total, m.question[:50], yp, np_, m.liquidity))
    near.sort()
    return markets, priced, near, dt

markets, priced, near, dt = asyncio.run(scan())
print(f"⚙️  Min-ask floor recheck (correct best-ask method): {priced} priced pairs in {dt:.1f}s")
print(f"📊 True near-misses (best-ask sum ≤1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if near:
    print(f"🏆 Best floor this run: sum={near[0][0]:.4f}")
else:
    print("🏆 Best floor this run: none ≤1.005")
