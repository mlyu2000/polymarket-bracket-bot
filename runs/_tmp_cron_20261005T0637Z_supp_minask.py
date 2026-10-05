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
    dt = time.time() - t0

    near = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if m.liquidity <= 0:
            continue
        # True best ask = min over ladder (asks list is DESC-sorted)
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total <= 1.005:
            near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    return markets, near, priced, dt

markets, near, priced, dt = asyncio.run(scan())
print(f"Supplement (best-ask via min): {priced} priced markets in {dt:.1f}s")
print(f"TRUE brackets (best-ask sum < 1.000): {sum(1 for t,*_ in near if t < 1.0)}")
print(f"Near-misses (sum <= 1.005): {len(near)}")
for total, q, yp, np_, liq in near[:10]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
if near:
    print(f"Floor: {near[0][0]:.4f}")
