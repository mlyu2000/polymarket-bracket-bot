import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    # /book asks are DESC-sorted; asks[0] is the WORST ask. Use min() for best ask.
    if not book or not getattr(book, 'asks', None):
        return None
    return min(float(a['price']) for a in book.asks)

async def main():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        ya, na = best_ask(yb), best_ask(nb)
        if ya is None or na is None:
            continue
        priced += 1
        rows.append((ya + na, m.question[:55], ya, na, m.liquidity))

    rows.sort()
    print(f"Best-ask check: {priced}/{len(markets)} markets priced in {dt:.1f}s")
    if rows:
        print(f"Floor (min sum of best asks): {rows[0][0]:.4f}")
        brackets = [r for r in rows if r[0] < 1.0]
        near = [r for r in rows if 1.0 <= r[0] <= 1.005]
        print(f"True brackets (<1.00): {len(brackets)}")
        print(f"Near-misses (1.000-1.005): {len(near)}")
        for total, q, ya, na, liq in rows[:8]:
            print(f"  {total:.4f} | Yes@{ya:.3f} No@{na:.3f} | liq={liq} | {q}")

asyncio.run(main())
