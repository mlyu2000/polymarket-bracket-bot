"""Supplementary: TRUE min-ask floor analysis (asks are DESC-sorted in /book;
asks[0] is the WORST ask, so the verbatim script's near-miss block is a known
artifact). Uses min(all asks) for both legs, plus tier counts and
two-sided/bracketability structural counts.
"""
import asyncio, logging, json, time
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
    elapsed = time.time() - t0

    def best(book):
        if not book or not book.asks:
            return None
        return min(float(a['price']) for a in book.asks)

    rows = []
    brackets_below_098 = 0
    tiers = {'le1.050': 0, 'le1.020': 0, 'le1.010': 0, 'le1.005': 0, 'lt1.000': 0}
    two_sided = 0
    both_asks = 0
    for m, (yb, nb) in zip(markets, all_books):
        y = best(yb)
        n = best(nb)
        if y is not None and n is not None:
            both_asks += 1
            tot = y + n
            rows.append((tot, m.question[:55], y, n, m.liquidity))
            if tot <= 1.050:
                tiers['le1.050'] += 1
            if tot <= 1.020:
                tiers['le1.020'] += 1
            if tot <= 1.010:
                tiers['le1.010'] += 1
            if tot <= 1.005:
                tiers['le1.005'] += 1
            if tot < 1.000:
                tiers['lt1.000'] += 1
            if tot <= 0.98:
                brackets_below_098 += 1
        if (yb and yb.bids and yb.asks) and (nb and nb.bids and nb.asks):
            two_sided += 1

    rows.sort()
    floor_top10 = [
        {'sum': round(r[0], 4), 'q': r[1], 'yes': round(r[2], 4), 'no': round(r[3], 4), 'liq': r[4]}
        for r in rows[:10]
    ]
    out = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'markets': len(markets),
        'with_both_asks': both_asks,
        'two_sided': two_sided,
        'not_bracketable': len(markets) - two_sided,
        'tiers': tiers,
        'brackets_below_098': brackets_below_098,
        'floor_top10': floor_top10,
        'top25': [
            {'total': round(r[0], 4), 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]}
            for r in rows[:25]
        ],
        'scan_time': round(elapsed, 1),
    }
    with open('runs/_tmp_cron_20261015T1305Z_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


asyncio.run(main())
