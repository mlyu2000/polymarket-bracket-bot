# cron supp scan: min-ask sums + book composition (detector-correct pricing)
import asyncio, logging, statistics
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    totals = []
    yes_only = two_sided = no_only = empty = 0
    for m, (yb, nb) in zip(markets, books):
        ya = yb.asks if yb else None
        na = nb.asks if nb else None
        if not ya and not na: empty += 1; continue
        if ya and not na: yes_only += 1; continue
        if na and not ya: no_only += 1; continue
        two_sided += 1
        y = min(float(a['price']) for a in ya); n = min(float(a['price']) for a in na)
        totals.append((y+n, m.question, y, n, m.liquidity))
    totals.sort()
    data = {'ts_utc': __import__('time').strftime('%Y-%m-%dT%H:%M:%SZ', __import__('time').gmtime()),
            'markets': len(markets), 'two_sided': two_sided, 'yes_only': yes_only,
            'no_only': no_only, 'empty': empty,
            'median': statistics.median(t[0] for t in totals),
            'bracketable_lt1': sum(1 for t in totals if t[0] < 1.0),
            'le_1005': sum(1 for t in totals if t[0] <= 1.005),
            'le_1010': sum(1 for t in totals if t[0] <= 1.01),
            'le_1050': sum(1 for t in totals if t[0] <= 1.05),
            'floor': [{'sum': t[0], 'q': t[1], 'yes': t[2], 'no': t[3], 'liq': t[4]} for t in totals[:10]]}
    import json
    out = f"runs/_tmp_cron_{__import__('os').environ.get('TS')}_supp_data.json"
    with open(out, 'w') as f: json.dump(data, f, indent=1)
    print(out)

import os
asyncio.run(main())
