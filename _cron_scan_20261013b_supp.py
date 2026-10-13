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

    floors = []          # (total, question, ymin, nmin, n_yasks, n_nasks, liquidity)
    two_sided = 0
    yes_only = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        two_sided += 1
        ymin = min(float(a['price']) for a in yb.asks)
        nmin = min(float(a['price']) for a in nb.asks)
        total = ymin + nmin
        floors.append((total, m.question[:60], ymin, nmin, len(yb.asks), len(nb.asks), m.liquidity))

    yes_only = len(markets) - two_sided
    floors.sort()

    bands = {}
    for cut in (1.005, 1.010, 1.020, 1.030, 1.050):
        bands[cut] = sum(1 for f in floors if f[0] <= cut)

    print(f"TRUE-FLOOR (min-ask) SCAN: {len(markets)} markets in {scan_time:.1f}s")
    print(f"two-sided={two_sided}  one-sided/no-asks={yes_only}")
    print(f"BRACKETS (true sum < 1.00): {sum(1 for f in floors if f[0] < 1.00)}")
    for total, q, ymin, nmin, ny, nn, liq in floors[:8]:
        if total >= 1.00:
            break
        print(f"  🔴 {total:.4f} | Y@{ymin:.3f}({ny} asks) N@{nmin:.3f}({nn} asks) | liq={liq:.0f} | {q}")
    print(f"TRUE near-miss floor (best 2-sided):")
    for total, q, ymin, nmin, ny, nn, liq in floors[:8]:
        print(f"  {total:.4f} | Y@{ymin:.3f}({ny}) N@{nmin:.3f}({nn}) | liq={liq:.0f} | {q}")
    print(f"bands: " + "  ".join(f"<={c}: n={n}" for c, n in bands.items()))
    n = len(floors)
    if n:
        med = floors[n // 2][0]
        print(f"median 2-sided min-ask floor: {med:.4f} (n={n})")
        print(f"not bracketable (sum>=1.005): {100.0 * (n - bands[1.005]) / n:.1f}%")

    with open('_cron_scan_20261013b_supp_data.json', 'w') as f:
        json.dump({
            'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            'markets': len(markets), 'two_sided': two_sided, 'one_sided': yes_only,
            'brackets_true': sum(1 for f in floors if f[0] < 1.00),
            'bands': bands,
            'median': (floors[n // 2][0] if n else None),
            'top': [{'total': t, 'q': q, 'y': y, 'n': nn, 'ny': a, 'nn': b, 'liq': l}
                    for t, q, y, nn, a, b, l in floors[:10]],
        }, f, indent=2)

asyncio.run(main())
