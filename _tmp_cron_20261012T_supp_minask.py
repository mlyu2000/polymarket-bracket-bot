import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    if not book or not book.asks:
        return None
    return min(float(a['price']) for a in book.asks)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, books):
        yp, np = best_ask(yb), best_ask(nb)
        if yp is not None and np is not None:
            two_sided += 1
            rows.append((yp + np, m.question[:70], yp, np, m.liquidity))
        elif yp is not None:
            yes_only += 1
        elif np is not None:
            no_only += 1
        else:
            empty += 1
    rows.sort()

    tiers = {}
    for thr in (1.005, 1.010, 1.020, 1.030, 1.050):
        tiers[thr] = sum(1 for r in rows if r[0] <= thr)

    below1 = [r for r in rows if r[0] < 1.0]
    band = [r for r in rows if r[0] <= 1.005]

    print(f"markets: {len(markets)} | two-sided: {two_sided} yes_only: {yes_only} no_only: {no_only} empty: {empty}")
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]}")
    print(f"  Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]}")
    print(f"brackets (sum<1.00): {len(below1)}")
    for t, q, yp, np, liq in below1[:10]:
        print(f"  <1.00 {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"band <=1.005: {len(band)}")
    for t, q, yp, np, liq in band[:8]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print("tier counts:", {f"<={k}": v for k, v in tiers.items()})
    if rows:
        print(f"best gross edge vs 1.00: {rows[0][0] - 1.0:+.4f} (0.98 actionable needs {1.0 - 0.98:.2f})")

    ts = time.strftime('%Y-%m-%dT%H%MZ', time.gmtime())
    entry = {
        'ts_utc': ts,
        'markets': len(markets),
        'brackets_verbatim': 0,
        'near_misses_verbatim_asks0': 0,
        'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only, 'empty': empty,
        'best_ask_floor': round(rows[0][0], 4) if rows else None,
        'floor_q': rows[0][1] if rows else None,
        'band_le_1005': len(band),
        'tiers': {str(k): v for k, v in tiers.items()},
        'best_gross_edge': round(rows[0][0] - 1.0, 4) if rows else None,
    }
    with open('results/cron_scan_history.jsonl', 'a') as f:
        f.write(json.dumps(entry) + '\n')
    with open(f'runs/_tmp_cron_{ts}_supp_data.json', 'w') as f:
        json.dump({'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only,
                   'empty': empty, 'floor': rows[0][0] if rows else None,
                   'band': [list(r) for r in band], 'tiers': tiers}, f)
    print('persisted history entry +', f'runs/_tmp_cron_{ts}_supp_data.json')

asyncio.run(supp())
