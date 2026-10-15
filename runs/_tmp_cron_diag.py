import asyncio, logging, time, json, bisect
from datetime import datetime, timezone
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def diag():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    det = BracketDetector()
    rows = []
    brackets = []
    two_sided = 0
    one_sided = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = det.detect(m, yes_book, no_book)
        if opp:
            brackets.append({
                'q': m.question, 'sum': opp.total_cost, 'yes': opp.yes_price,
                'no': opp.no_price, 'edge': opp.net_edge, 'shares': opp.max_shares,
                'liq': m.liquidity,
            })
        if yes_book and no_book and yes_book.asks and no_book.asks:
            two_sided += 1
            y_min = min(float(a['price']) for a in yes_book.asks)
            n_min = min(float(a['price']) for a in no_book.asks)
            total = y_min + n_min
            rows.append((round(total, 6), m.question, y_min, n_min, m.liquidity))
        else:
            one_sided += 1

    rows.sort()
    totals = [r[0] for r in rows]
    def count_le(x):
        return bisect.bisect_right(totals, x)
    tiers = {
        'le1.005': count_le(1.005), 'le1.010': count_le(1.010),
        'le1.020': count_le(1.020), 'le1.050': count_le(1.050),
        'lt1.000': count_le(0.99999),
    }
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = {
        'timestamp': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'markets': len(markets), 'scan_time_s': round(scan_time, 1),
        'brackets': brackets,
        'two_sided': two_sided, 'one_sided': one_sided,
        'floor': rows[0][0] if rows else None,
        'top10': rows[:10],
        'tiers': tiers,
    }
    fname = f'runs/_tmp_cron_{ts}_supp_data.json'
    with open(fname, 'w') as f:
        json.dump(out, f, indent=1)
    print('saved', fname)
    print(json.dumps({k: v for k, v in out.items() if k not in ('top10', 'brackets')}, indent=1))
    print('--- top10 (min-ask floor) ---')
    for t, q, y, n, liq in rows[:10]:
        print(f'{t:.3f} | Yes@{y:.3f} No@{n:.3f} | liq {liq:,.0f} | {q}')
    print('--- brackets (detector) ---')
    for b in brackets:
        print(b)

asyncio.run(diag())
