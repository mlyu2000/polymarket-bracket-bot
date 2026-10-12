import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    elapsed = time.time() - t0

    priced = 0
    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            priced += 1
            totals.append((ya + na, m.question[:60], ya, na, m.liquidity))
    totals.sort()
    print(f"min-ask supplemental | {len(markets)} markets, {priced} priced, {elapsed:.1f}s")
    below_1 = [t for t in totals if t[0] < 1.0]
    print(f"min-ask brackets (sum<1.00): {len(below_1)}")
    for total, q, ya, na, liq in below_1:
        print(f"  *** {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    nm = [t for t in totals if 1.0 <= t[0] <= 1.005]
    print(f"min-ask near-misses (1.000-1.005): {len(nm)}")
    for total, q, ya, na, liq in nm[:5]:
        print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")
    if totals:
        print(f"true floor (min sum across priced markets): {totals[0][0]:.4f} | {totals[0][1]}")

asyncio.run(supp())
