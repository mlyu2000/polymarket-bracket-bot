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
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        has_y = bool(yb and yb.asks)
        has_n = bool(nb and nb.asks)
        if not has_y and not has_n:
            empty += 1
            continue
        if has_y and has_n:
            two_sided += 1
            yp = min(float(a['price']) for a in yb.asks)
            np = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
        elif has_y:
            yes_only += 1
        else:
            no_only += 1
    rows.sort()
    n = len(rows)
    median = rows[n // 2][0] if n else None
    print(f"SCAN: {len(markets)} markets in {scan_time:.1f}s")
    print(f"MIN-ASK FLOOR (min of ALL asks, both sides):")
    for total, q, yp, np, liq in rows[:5]:
        print(f"  {total:.4f} | Yes@{yp:.4f} No@{np:.4f} | liq {liq:,.0f} | {q}")
    print(f"TOTALS: <=1.005={sum(1 for r in rows if r[0]<=1.005)} <=1.010={sum(1 for r in rows if r[0]<=1.010)} <=1.020={sum(1 for r in rows if r[0]<=1.020)} <=1.030={sum(1 for r in rows if r[0]<=1.030)} <=1.050={sum(1 for r in rows if r[0]<=1.050)}")
    print(f"BOOKS: two-sided={two_sided} yes-only={yes_only} no-only={no_only} empty={empty}")
    print(f"MEDIAN two-sided min-ask sum: {median:.4f}" if median else "MEDIAN: n/a")
    with open('runs/_tmp_cron_supp_data.json', 'w') as f:
        json.dump({'scan_time': scan_time, 'two_sided': two_sided, 'yes_only': yes_only,
                   'no_only': no_only, 'empty': empty, 'median': median,
                   'top': rows[:10]}, f, indent=2)

asyncio.run(scan())
