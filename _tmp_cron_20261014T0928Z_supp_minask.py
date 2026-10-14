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
    tiers = {'<=1.050': 0, '<=1.020': 0, '<=1.010': 0, '<=1.005': 0, '<1.000': 0}
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
                tiers['<=1.050'] += 1
            if tot <= 1.020:
                tiers['<=1.020'] += 1
            if tot <= 1.010:
                tiers['<=1.010'] += 1
            if tot <= 1.005:
                tiers['<=1.005'] += 1
            if tot < 1.000:
                tiers['<1.000'] += 1
        if (yb and yb.bids and yb.asks) and (nb and nb.bids and nb.asks):
            two_sided += 1

    rows.sort()
    out = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'markets': len(markets),
        'with_both_asks': both_asks,
        'two_sided': two_sided,
        'not_bracketable': len(markets) - two_sided,
        'tiers': tiers,
        'scan_time': round(elapsed, 1),
        'top25': [
            {'total': round(r[0], 4), 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]}
            for r in rows[:25]
        ],
    }
    with open('runs/_tmp_cron_20261014T0928Z_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(f"ts={out['ts']} markets={out['markets']} both_asks={both_asks} two_sided={two_sided} not_bracketable={out['not_bracketable']} time={elapsed:.1f}s")
    print("TIERS:", json.dumps(tiers))
    print("TOP 15 (min-ask floor):")
    for r in rows[:15]:
        print(f"  {r[0]:.4f} | Y@{r[2]:.4f} N@{r[3]:.4f} | liq={r[4]:>10.1f} | {r[1]}")


asyncio.run(main())
