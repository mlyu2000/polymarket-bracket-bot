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
    both = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(yes_ask["price"]); np_ = float(no_ask["price"])
        total = yp + np_
        both += 1
        rows.append((round(total, 6), m.question[:60], yp, np_, m.liquidity,
                     int(float(yes_ask["size"])), int(float(no_ask["size"]))))
    rows.sort()
    near = [r for r in rows if r[0] <= 1.005]
    under = [r for r in rows if r[0] < 1.0]
    band = [r for r in rows if r[0] <= 1.010]

    out = {
        'markets': len(markets),
        'both_sides_priced': both,
        'scan_time': round(scan_time, 1),
        'best_ask_floor': rows[0] if rows else None,
        'sum_lt_1_00': under,
        'near_le_1_005': near,
        'band_le_1_010_count': len(band),
        'top12': rows[:12],
    }
    with open('_tmp_cron_20261005T1232Z_supp_data.json', 'w') as f:
        json.dump(out, f, indent=1)

    print(f"supp scan {len(markets)} markets {scan_time:.1f}s; both_sides_priced={both}")
    if rows:
        print(f"TRUE best-ask floor sum: {rows[0][0]:.4f} | {rows[0][1]} (Yes@{rows[0][2]:.3f} x{rows[0][5]} No@{rows[0][3]:.3f} x{rows[0][6]} liq={rows[0][4]})")
    print(f"sum<1.00 (best-ask): {len(under)}")
    print(f"near (<=1.005, best-ask): {len(near)}")
    for r in near[:8]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} x{r[5]} No@{r[3]:.3f} x{r[6]} | liq={r[4]} | {r[1]}")
    print(f"band <=1.010 count: {len(band)}")
    print("top-12 lowest best-ask sums:")
    for r in rows[:12]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} x{r[5]} No@{r[3]:.3f} x{r[6]} | liq={r[4]} | {r[1]}")

asyncio.run(scan())
