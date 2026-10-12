"""Comprehensive 20261012T1536Z supplement: full two-sided min-ask rows,
tier counts, median, and structural (bracket-ability @0.98) breakdown.
Persists runs/_tmp_cron_20261012T1536Z_supp_data.json.
"""
import asyncio
import json
import logging
import os

from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

THRESH = 0.98
OUT = os.path.join(os.path.dirname(__file__), "runs", "_tmp_cron_20261012T1536Z_supp_data.json")


async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    # structural (bracket-ability @0.98) over ALL markets
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        yb_asks = yb.asks if yb else []
        nb_asks = nb.asks if nb else []
        ymin = min((float(a['price']) for a in yb_asks), default=None)
        nmin = min((float(a['price']) for a in nb_asks), default=None)

        y_ok = ymin is not None and ymin < THRESH
        n_ok = nmin is not None and nmin < THRESH
        if y_ok and n_ok:
            two_sided += 1
        elif y_ok and not n_ok:
            yes_only += 1
        elif n_ok and not y_ok:
            no_only += 1
        else:
            empty += 1

        if ymin is not None and nmin is not None:
            rows.append({
                'q': m.question[:55],
                'yes_min': round(ymin, 4),
                'no_min': round(nmin, 4),
                'total': round(ymin + nmin, 4),
                'liq': round(m.liquidity, 4),
                'n_yes_asks': len(yb_asks),
                'n_no_asks': len(nb_asks),
            })
    rows.sort(key=lambda r: r['total'])
    return markets, rows, {'two_sided': two_sided, 'yes_only': yes_only,
                           'no_only': no_only, 'empty': empty}


async def main():
    markets, rows, struct = await scan()
    totals = [r['total'] for r in rows]
    n = len(totals)
    tiers = {
        'le1005': sum(1 for t in totals if t <= 1.005),
        'le1010': sum(1 for t in totals if t <= 1.010),
        'le1020': sum(1 for t in totals if t <= 1.020),
        'le1030': sum(1 for t in totals if t <= 1.030),
    }
    if n:
        median = (totals[n // 2] if n % 2 else round((totals[n//2 - 1] + totals[n//2]) / 2, 4))
    else:
        median = None

    payload = {
        'ts': '20261012T1536Z',
        'markets': len(markets),
        'two_sided_priced': n,
        'floor': rows[0] if rows else None,
        'tiers': tiers,
        'median': median,
        'structural': struct,
        'rows': rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    # sidecar summary
    with open(OUT.replace('_supp_data.json', '_summary.json'), 'w') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"markets={len(markets)} two_sided_priced={n}")
    print(f"FLOOR: {rows[0]['total']:.4f} | {rows[0]['q']} | Y@{rows[0]['yes_min']} N@{rows[0]['no_min']} liq={rows[0]['liq']:.0f}")
    print(f"tiers: {tiers} | median={median}")
    print(f"structural(@0.98 bracket-ability): {struct} not_bracketable_pct={round((1-struct['two_sided']/len(markets))*100,1)}")
    print(f"persisted: {OUT}")


asyncio.run(main())
