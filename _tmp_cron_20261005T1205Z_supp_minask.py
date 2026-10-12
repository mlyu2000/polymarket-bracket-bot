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

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        priced += 1
        y = min(float(a['price']) for a in yes_book.asks)
        n = min(float(a['price']) for a in no_book.asks)
        rows.append((y + n, m.question[:60], y, n, m.liquidity))

    rows.sort()
    print(f"[supp] best-ask totals over {priced}/{len(markets)} priced markets in {dt:.1f}s")
    print(f"[supp] brackets sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print(f"[supp] <=1.005: {sum(1 for r in rows if r[0] <= 1.005)}")
    for total, q, yp, np, liq in rows[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    with open('_tmp_cron_20261005T1205Z_supp_data.json', 'w') as f:
        json.dump(rows[:20], f)

asyncio.run(scan())
