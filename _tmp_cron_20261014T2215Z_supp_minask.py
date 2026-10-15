"""Supplementary: true min-ask floor + tier stats + structural bracket-ability.
Floor = min(all asks) on BOTH legs (task-script near-miss uses asks[0] which is
DESC-sorted = worst ask, artifact that always reports 0). Persists supp_data.json.
"""
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

    two_sided = 0
    rows = []  # (total, q, yp, np, liq, end, cond, no_ask_max)
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            two_sided += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            if yp < 1.0 and np_ < 1.0 and yp > 0 and np_ > 0:
                no_max = max(float(a['price']) for a in nb.asks)
                rows.append((yp + np_, m.question, yp, np_, m.liquidity,
                             getattr(m, 'end_date', ''), getattr(m, 'condition_id', ''), no_max))

    rows.sort()
    floor = rows[0] if rows else None

    tiers = {}
    for thr in (1.050, 1.020, 1.010, 1.005, 1.000):
        tiers[f'le{thr}'] = sum(1 for r in rows if r[0] <= thr)
    tiers['lt1.000'] = sum(1 for r in rows if r[0] < 1.0)

    # structural: two-sided with NO min-ask >= 0.99 on either leg -> unbuildable
    no_high = sum(1 for r in rows if r[7] < 0.99)
    bracketable = two_sided - no_high

    out = {
        'scan_time': round(scan_time, 1),
        'markets': len(markets),
        'two_sided': two_sided,
        'yes_only': len(markets) - two_sided,
        'no_ask_max_lt099': no_high,
        'bracketable': bracketable,
        'tiers': tiers,
        'floor': {
            'total': round(floor[0], 4),
            'q': floor[1][:60],
            'yes': floor[2], 'no': floor[3],
            'liq': floor[4], 'end': str(floor[5]), 'cond': floor[6],
        } if floor else None,
        'le1010': [
            {'total': round(r[0], 4), 'q': r[1][:55], 'y': r[2], 'n': r[3], 'liq': r[4]}
            for r in rows[:10]
        ],
    }
    print(json.dumps(out, indent=1))
    with open('_tmp_cron_20261014T2215Z_supp_data.json', 'w') as f:
        json.dump(out, f)

asyncio.run(main())
