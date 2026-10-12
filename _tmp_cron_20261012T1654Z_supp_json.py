# Supplementary data export: true best-ask floors, tier counts, structural split.
# CLOB /book asks are DESC-sorted; asks[0] = worst ask. All floors use min(asks).
import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    t0 = time.time()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    two_sided = yes_only = no_only = both_empty = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        y_as = yes_book.asks if yes_book else []
        n_as = no_book.asks if no_book else []
        if y_as and n_as:
            two_sided += 1
        elif y_as and not n_as:
            yes_only += 1
        elif n_as and not y_as:
            no_only += 1
        else:
            both_empty += 1
            continue
        if y_as and n_as:
            yp = min(float(a['price']) for a in y_as)
            np_ = min(float(a['price']) for a in n_as)
            rows.append((yp + np_, m.question, yp, np_, m.liquidity))
    rows.sort()
    return {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'scan_time_s': round(scan_time, 1),
        'markets': len(markets),
        'priced': len(rows),
        'structural': {'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only, 'both_empty': both_empty},
        'floors': [[round(t, 4), q, y, n, round(l, 2)] for t, q, y, n, l in rows[:10]],
        'entries': [{'total': round(t, 4), 'q': q, 'yes': y, 'no': n, 'liq': round(l, 2)}
                    for t, q, y, n, l in rows if t <= 1.005],
        'tiers': {
            'le_1000': sum(1 for t, *_ in rows if t <= 1.000),
            'le_1005': sum(1 for t, *_ in rows if t <= 1.005),
            'le_1010': sum(1 for t, *_ in rows if t <= 1.010),
            'le_1020': sum(1 for t, *_ in rows if t <= 1.020),
            'le_1030': sum(1 for t, *_ in rows if t <= 1.030),
        },
        'floor': {'total': round(rows[0][0], 4), 'q': rows[0][1], 'yes': rows[0][2],
                  'no': rows[0][3], 'liq': round(rows[0][4], 2)} if rows else None,
    }

out = asyncio.run(scan())
with open('runs/_tmp_cron_20261012T1654Z_supp_data.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"markets={out['markets']} priced={out['priced']} scan={out['scan_time_s']}s structural={out['structural']}")
print(f"floor={out['floor']}")
print(f"tiers={out['tiers']}")
print("top floors:")
for t, q, y, n, l in out['floors'][:8]:
    print(f"  {t:.4f} | Y@{y:.3f} N@{n:.3f} | liq={l} | {q[:60]}")
