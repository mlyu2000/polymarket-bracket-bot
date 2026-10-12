"""Supplementary min-ask scan — computes the TRUE bracket floor using min(all asks),
because Polymarket /book returns asks DESC-sorted (asks[0] = worst ask).
Also captures structural bracket-ability stats and tier counts.
Persists results to runs/_tmp_cron_20261012T232021Z_supp_data.json.
"""
import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    floors = []          # (total, q, yp, np, liq) with both books having asks
    tiers = {'le1000': 0, 'le1005': 0, 'le1010': 0, 'le1020': 0, 'le1030': 0, 'le1050': 0}
    structural = {'two_sided': 0, 'yes_only': 0, 'no_only': 0, 'empty': 0}
    entries = []
    for m, (yb, nb) in zip(markets, books):
        has_y = bool(yb and yb.asks)
        has_n = bool(nb and nb.asks)
        if has_y and has_n:
            structural['two_sided'] += 1
        elif has_y:
            structural['yes_only'] += 1
        elif has_n:
            structural['no_only'] += 1
        else:
            structural['empty'] += 1
        if has_y and has_n:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = yp + np_
            if total <= 1.03:
                tiers['le1030'] += 1
            if total <= 1.05:
                tiers['le1050'] += 1
            if total <= 1.02:
                tiers['le1020'] += 1
            if total <= 1.01:
                tiers['le1010'] += 1
            if total <= 1.005:
                tiers['le1005'] += 1
            if total < 1.0:
                tiers['le1000'] += 1
            if total <= 1.03:
                floors.append((round(total, 4), m.question[:60], round(yp, 4), round(np_, 4), m.liquidity))
                entries.append({
                    'total': round(total, 4),
                    'q': m.question[:80],
                    'yes': round(yp, 4),
                    'no': round(np_, 4),
                    'liq': m.liquidity,
                })
    floors.sort()
    entries.sort(key=lambda e: e['total'])
    out = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'markets': len(markets),
        'floors': floors[:10],
        'entries': entries[:10],
        'tiers': tiers,
        'structural': structural,
    }
    with open('runs/_tmp_cron_20261012T232021Z_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

asyncio.run(supp())
