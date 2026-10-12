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
    scored = []
    brackets = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        if total < 1.0:
            brackets += 1
        scored.append((total, m.question[:55], yp, np_, m.liquidity))
    scored.sort()
    print(f"fetch {len(markets)} mkts in {dt:.1f}s | true brackets(best-ask sum<1.00): {brackets}")
    print("top-8 lowest best-ask sums:")
    for total, q, yp, np_, liq in scored[:8]:
        print(f"  {total:.4f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq} | {q}")
    nm = [s for s in scored if s[0] <= 1.005]
    print(f"near-misses <=1.005 (best-ask): {len(nm)}")

asyncio.run(scan())
