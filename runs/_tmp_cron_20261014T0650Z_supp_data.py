import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    print(f"scan_time={time.time()-t0:.1f}s markets={len(markets)}")

    def min_ask(book):
        if not book or not book.asks:
            return None
        return min(float(a['price']) for a in book.asks)

    floors = []
    twosided = yes_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        ya, na = min_ask(yb), min_ask(nb)
        if ya is None and na is None:
            empty += 1
        elif ya is None or na is None:
            yes_only += 1
        else:
            twosided += 1
            floors.append((ya + na, m.question[:60], ya, na, m.liquidity))

    floors.sort()
    print(f"two_sided={twosided} yes_or_no_only={yes_only} empty={empty}")
    print(f"true_min_ask_floor={floors[0][0]:.4f}")
    n010 = sum(1 for f in floors if f[0] <= 1.010)
    n020 = sum(1 for f in floors if f[0] <= 1.020)
    n050 = sum(1 for f in floors if f[0] <= 1.050)
    print(f"<=1.050: {n050} | <=1.020: {n020} | <=1.010: {n010}")
    print("--- top 8 closest ---")
    for total, q, ya, na, liq in floors[:8]:
        print(f"  {total:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq} | {q}")
    print("--- bracketable (floor < 1.00) ---")
    brk = [f for f in floors if f[0] < 1.00]
    print(f"count={len(brk)}")
    for total, q, ya, na, liq in brk[:10]:
        print(f"  🔴 {total:.4f} | Y@{ya:.3f} N@{na:.3f} | liq={liq} | {q}")

asyncio.run(main())
