import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def run():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = yp + np_
            rows.append((total, m.question[:60], yp, np_, len(yb.asks), len(nb.asks), m.liquidity, m.clob_token_ids))
    rows.sort()

    brackets = [r for r in rows if r[0] < 1.00]
    bands = {}
    for th in (1.001, 1.002, 1.003, 1.004, 1.005, 1.010, 1.015, 1.020, 1.030, 1.050):
        bands[th] = sum(1 for r in rows if r[0] <= th)
    two_sided = len(rows)

    print(f"Scan: {len(markets)} markets in {scan_time:.1f}s | two-sided: {two_sided} ({100*(1-two_sided/len(markets)):.1f}% not bracketable)")
    print(f"TRUE FLOOR (min-ask both sides): {rows[0][0]:.4f}" if rows else "no rows")
    print(f"BRACKETS (sum<1.00): {len(brackets)}")
    for r in brackets[:10]:
        print(f"  RED {r[0]:.4f} Y@{r[2]:.4f} N@{r[3]:.4f} | {r[1]}")
    print("Bands:", {k: v for k, v in bands.items()})
    print("Top 10 floors:")
    for r in rows[:10]:
        print(f"  {r[0]:.4f} | Y@{r[2]:.4f} ({r[4]} asks) N@{r[3]:.4f} ({r[5]} asks) | liq {r[6]:.0f} | {r[1]}")

    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    data = {
        'timestamp': ts,
        'markets_scanned': len(markets),
        'two_sided': two_sided,
        'floor': rows[0][0] if rows else None,
        'brackets': len(brackets),
        'bands': bands,
        'median': rows[len(rows)//2][0] if rows else None,
        'top': [{'total': r[0], 'q': r[1], 'yes': r[2], 'no': r[3], 'y_asks': r[4], 'n_asks': r[5], 'liq': r[6], 'tokens': r[7]} for r in rows[:20]],
    }
    with open(f'runs/_tmp_cron_{ts}_supp_data.json', 'w') as f:
        json.dump(data, f, indent=1)
    print(f"saved runs/_tmp_cron_{ts}_supp_data.json")

asyncio.run(run())
