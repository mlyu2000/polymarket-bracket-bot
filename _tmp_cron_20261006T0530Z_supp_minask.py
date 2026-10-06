import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))

    rows.sort()
    print(f"priced markets: {priced} / {len(markets)}")
    print("best (lowest yes+no ask sums, min-ask method):")
    for total, q, yp, np, liq in rows[:8]:
        flag = "ARB<1.00" if total < 1.0 else ("near<=1.005" if total <= 1.005 else "")
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {flag} | {q}")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"true brackets (sum<1.000): {len(brackets)}")
    band = [r for r in rows if r[0] <= 1.005]
    print(f"band <=1.005 count: {len(band)}")
    with open('_tmp_cron_20261006T0530Z_supp_data.json', 'w') as f:
        json.dump({'priced': priced, 'top': rows[:12]}, f)

asyncio.run(scan())
