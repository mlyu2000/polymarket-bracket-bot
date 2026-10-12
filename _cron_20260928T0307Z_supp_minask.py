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
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    print(f"SUPP best-ask scan: {len(markets)} markets, {priced} priced, {dt:.1f}s")
    print(f"Min possible-pair-sum: {rows[0][0]:.3f}" if rows else "no priced markets")
    brackets = [r for r in rows if r[0] < 1.0]
    print(f"Pairs with sum<1.00 (best ask): {len(brackets)}")
    for r in brackets[:10]:
        print(f"  {r[0]:.3f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    print("Top 5 cheapest sums:")
    for r in rows[:5]:
        print(f"  {r[0]:.3f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"Near-miss band 1.000-1.005 (best ask): {len(nm)}")
    for r in nm[:5]:
        print(f"  {r[0]:.3f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    out = {
        'scan': '20260928T0307Z',
        'markets_fetched': len(markets),
        'priced_markets_best_ask': priced,
        'brackets_sum_lt_1': len(brackets),
        'near_miss_le_1p005': len(nm),
        'min_best_ask_sum': rows[0][0] if rows else None,
        'near_misses': [{'sum': r[0], 'yes': r[2], 'no': r[3], 'liq': r[4], 'q': r[1]} for r in nm[:10]],
        'scan_time_s': round(dt, 1),
    }
    with open('runs/scan_20260928T0307Z_floor.json', 'w') as f:
        json.dump(out, f, indent=1)
    print("saved runs/scan_20260928T0307Z_floor.json")

asyncio.run(scan())
