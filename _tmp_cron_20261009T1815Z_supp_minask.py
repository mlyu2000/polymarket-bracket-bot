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
    scan_time = time.time() - t0

    rows = []
    priced = 0
    skipped = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            skipped += 1
            continue
        if m.liquidity <= 0:
            skipped += 1
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        priced += 1
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    json.dump({'markets': len(markets), 'priced': priced, 'skipped': skipped,
               't': scan_time, 'near': [[round(t,4), q, yp, np, liq] for t, q, yp, np, liq in rows[:60]]},
              open('_tmp_cron_20261009T1815Z_supp_data.json', 'w'))
    print(f"SUPP best-ask scan: {len(markets)} markets, {priced} priced, {skipped} skipped, {scan_time:.1f}s")
    print("--- TRUE best-ask sums <= 1.005 (near-misses) ---")
    n = 0
    for total, q, yp, np_, liq in rows:
        if total <= 1.005:
            n += 1
            print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
    print(f"near-miss total count: {n}")
    print("--- 8 lowest best-ask sums overall ---")
    for total, q, yp, np_, liq in rows[:8]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")

asyncio.run(scan())
