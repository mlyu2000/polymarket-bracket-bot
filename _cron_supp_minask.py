import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    two_sided = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        two_sided += 1
        ya = [float(a['price']) for a in yb.asks]
        na = [float(a['price']) for a in nb.asks]
        floor = min(ya) + min(na)
        rows.append((floor, m.question[:60], min(ya), min(na), m.liquidity, len(ya), len(na)))
    rows.sort()

    brackets = [r for r in rows if r[0] < 1.0]
    tiers = {}
    for t in (1.005, 1.010, 1.020, 1.050):
        tiers[t] = sum(1 for r in rows if r[0] <= t)

    out = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'scan_time': scan_time,
        'markets': len(markets),
        'two_sided': two_sided,
        'not_bracketable': len(markets) - two_sided,
        'brackets': brackets,
        'tiers': {str(k): v for k, v in tiers.items()},
        'top20': [
            {'floor': r[0], 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4], 'n_asks_y': r[5], 'n_asks_n': r[6]}
            for r in rows[:20]
        ],
    }
    with open('_cron_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)

    print(f"markets={len(markets)} two_sided={two_sided} not_bracketable={out['not_bracketable']} scan={scan_time:.1f}s")
    print(f"brackets(<1.00, min-ask): {len(brackets)}")
    for b in brackets:
        print(f"  BRACKET {b[0]:.4f} | Y@{b[2]:.3f} N@{b[3]:.3f} | {b[1]}")
    print("top-20 min-ask floors:")
    for r in rows[:20]:
        print(f"  {r[0]:.4f} | Y@{r[2]:.3f} N@{r[3]:.3f} | liq {r[4]} | {r[1]}")
    print("tiers:", {str(k): v for k, v in tiers.items()})

asyncio.run(main())
