import asyncio, logging, time, json
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

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(float(a['price']) for a in yes_book.asks)
            no_ask = min(float(a['price']) for a in no_book.asks)
            total = yes_ask + no_ask
            rows.append((total, m.question[:60], yes_ask, no_ask, m.liquidity))
    rows.sort()
    print(f"min-ask check: {len(rows)} markets with both books, {scan_time:.1f}s")
    print("best 10 sums (min yes ask + min no ask):")
    for total, q, yp, np, liq in rows[:10]:
        flag = "LT1" if total < 1.0 else ("LE1.005" if total <= 1.005 else "")
        print(f"  {total:.4f} {flag} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    with open('_tmp_cron_20261009T1147Z_supp_data.json', 'w') as f:
        json.dump({'best_rows': rows[:20], 'count_lt1': sum(1 for r in rows if r[0] < 1.0),
                   'count_le1005': sum(1 for r in rows if r[0] <= 1.005)}, f)

asyncio.run(supp())
