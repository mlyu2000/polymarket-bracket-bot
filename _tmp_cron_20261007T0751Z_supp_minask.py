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
    results = []
    n_no_asks = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask0 = float(yes_book.asks[0]['price'])
            no_ask0 = float(no_book.asks[0]['price'])
            yes_min = min(float(a['price']) for a in yes_book.asks)
            no_min = min(float(a['price']) for a in no_book.asks)
            total_min = yes_min + no_min
            if total_min <= 1.005:
                results.append((total_min, m.question[:55], yes_min, no_min, yes_ask0, no_ask0, m.liquidity))
        else:
            n_no_asks += 1
    results.sort()
    print(f"min-ask check over {len(markets)} markets in {dt:.1f}s (books missing asks: {n_no_asks})")
    print(f"TRUE near-misses (min-ask sum <=1.005): {len(results)}")
    for total, q, ym, nm, ya, na, liq in results[:10]:
        print(f"  {total:.3f} | YesMin@{ym:.3f} NoMin@{nm:.3f} (ask0 {ya:.3f}/{na:.3f}) | liq={liq} | {q}")

asyncio.run(scan())
