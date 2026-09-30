import asyncio, logging, json, time
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
    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append((round(yp + np_, 4), yp, np_, m.question[:60], m.liquidity))
    rows.sort()
    return len(markets), rows, time.time() - t0

n, rows, dt = asyncio.run(scan())
priced = len(rows)
brackets = [r for r in rows if r[0] < 1.00]
near = [r for r in rows if 1.00 <= r[0] <= 1.005]
print(f"markets={n} priced={priced} scan={dt:.1f}s")
print(f"BRACKETS (best-ask sum<1.00): {len(brackets)}")
for r in brackets[:10]:
    print(f"  {r[0]:.4f} | Yes@{r[1]:.3f} No@{r[2]:.3f} | liq={r[4]} | {r[3]}")
print(f"NEAR (1.00<=sum<=1.005): {len(near)}")
for r in near[:10]:
    print(f"  {r[0]:.4f} | Yes@{r[1]:.3f} No@{r[2]:.3f} | liq={r[4]} | {r[3]}")
print("FLOOR top-8:")
for r in rows[:8]:
    print(f"  {r[0]:.4f} | {r[3]}")
out = {'ts': '$TS', 'markets': n, 'priced': priced,
       'brackets': [list(b) for b in brackets],
       'near': [list(x) for x in near],
       'top_min_ask_sums': [list(r) for r in rows[:10]]}
json.dump(out, open('runs/scan_20260929T050245Z.json', 'w'), indent=1)
