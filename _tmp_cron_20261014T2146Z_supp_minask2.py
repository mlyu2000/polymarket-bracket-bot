"""Supplementary #2: precise NO-leg distribution + bracketability count
(NO min-ask >= 0.99 => YES leg is a near-dust long-shot, bracket not
realistically buildable; NO < 0.99 => both legs have real price).
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
    no_ge_099 = 0
    no_lt_099 = 0
    both_asks = 0
    for m, (yb, nb) in zip(markets, all_books):
        y = best(yb)
        n = best(nb)
        if y is not None and n is not None:
            both_asks += 1
            tot = y + n
            rows.append((tot, m.question[:55], y, n, m.liquidity))
            if n >= 0.99:
                no_ge_099 += 1
            else:
                no_lt_099 += 1
    rows.sort()
    out = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'markets': len(markets),
        'with_both_asks': both_asks,
        'no_ge_099': no_ge_099,
        'no_lt_099_bracketable': no_lt_099,
        'bracketable_min_total': round(min(r[0] for r in rows if r[3] < 0.99), 4) if no_lt_099 else None,
        'top_bracketable': [
            {'total': round(r[0], 4), 'q': r[1], 'yes': r[2], 'no': r[3], 'liq': r[4]}
            for r in rows if r[3] < 0.99
        ][:10],
        'scan_time': round(elapsed, 1),
    }
    with open('runs/_tmp_cron_20261014T2146Z_supp_data2.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


asyncio.run(main())
