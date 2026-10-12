import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np_, m.question[:55], yp, np_, m.liquidity))

    sums.sort()
    priced = len(sums)
    brackets = [s for s in sums if s[0] < 1.0]
    near = [s for s in sums if s[0] <= 1.005]
    print(f"BEST-ASK FLOOR CHECK: {priced}/{len(markets)} markets priced")
    print(f"True brackets (sum<1.00): {len(brackets)}")
    for t, q, yp, np_, liq in brackets[:10]:
        print(f"  🔴 {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"Near-misses (≤1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:8]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if sums:
        print(f"Floor: {sums[0][0]:.4f} | median: {sums[len(sums)//2][0]:.4f}")

asyncio.run(scan())
