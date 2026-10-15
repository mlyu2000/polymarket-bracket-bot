import asyncio, json, logging, time
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
    two_sided = 0
    yes_only = 0
    no_only = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            if (yb and yb.asks) or (nb and nb.asks):
                yes_only += 1 if (yb and yb.asks) else 0
                no_only += 1 if (nb and nb.asks) else 0
            continue
        y = min(float(a['price']) for a in yb.asks)
        n = min(float(a['price']) for a in nb.asks)
        two_sided += 1
        rows.append((y + n, m.question[:60], y, n, m.liquidity))

    rows.sort()
    return {
        'markets': len(markets),
        'two_sided': two_sided,
        'yes_only': yes_only,
        'no_only': no_only,
        'rows': rows,
        'scan_time': scan_time,
    }

result = asyncio.run(scan())
ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
out = {
    'ts': ts,
    'markets': result['markets'],
    'two_sided': result['two_sided'],
    'yes_only': result['yes_only'],
    'no_only': result['no_only'],
    'scan_time': round(result['scan_time'], 1),
    'floor': result['rows'][0] if result['rows'] else None,
    'top10': result['rows'][:10],
}
with open(f'runs/_tmp_cron_{ts}_supp_data.json', 'w') as f:
    json.dump(out, f, indent=2)

print(f"🔍 Scan: {result['markets']} markets in {result['scan_time']:.1f}s")
print(f"Two-sided: {result['two_sided']} | yes-only: {result['yes_only']} | no-only: {result['no_only']}")
if result['rows']:
    print(f"FLOOR (min-ask both sides): {result['rows'][0][0]:.3f} | {result['rows'][0][1]} | Y{result['rows'][0][2]:.3f}+N{result['rows'][0][3]:.3f} | liq {result['rows'][0][4]:.0f}")
    print("Top 10:")
    for total, q, y, n, liq in result['rows'][:10]:
        print(f"  {total:.3f} | Y{y:.3f} N{n:.3f} | liq {liq:.0f} | {q}")
    for cut in (1.050, 1.020, 1.010, 1.005):
        print(f"  <= {cut:.3f}: n={sum(1 for r in result['rows'] if r[0] <= cut)}")
