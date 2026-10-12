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
    scan_time = time.time() - t0

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            sums.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    sums.sort()
    print(f"Supp (min-ask): {len(markets)} markets, {len(sums)} priced, in {scan_time:.1f}s")
    brackets = [s for s in sums if s[0] < 1.0]
    near = [s for s in sums if 1.0 <= s[0] <= 1.005]
    print(f"TRUE brackets (min-ask sum < 1.000): {len(brackets)}")
    for total, q, yp, np, liq in brackets[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"Near-misses 1.000-1.005: {len(near)}")
    for total, q, yp, np, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    if sums:
        print(f"Floor (best sum overall): {sums[0][0]:.4f} | {sums[0][1]}")

asyncio.run(supp())
