"""Supplementary: best-ask (min) based totals for near-miss analysis.
Polymarket /book returns asks DESC-sorted (asks[0] = worst ask ~0.999).
The verbatim prompt script's near-miss block using asks[0] always reports 0.
This computes the true min-ask floor, tier histogram, two-sided count,
not-bracketable count, and per-leader details.

"""
import asyncio, json, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)


async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    two_sided = 0
    yes_only = 0
    na_only = 0
    not_bracketable = 0
    for m, (yb, nb) in zip(markets, all_books):
        ya = [float(a['price']) for a in yb.asks] if yb and yb.asks else []
        na = [float(a['price']) for a in nb.asks] if nb and nb.asks else []
        if ya and na:
            two_sided += 1
            yp, np_ = min(ya), min(na)
            rows.append((yp + np_, m.question[:80], yp, np_, m.liquidity))
        elif ya:
            yes_only += 1
            not_bracketable += 1
        elif na:
            na_only += 1
            not_bracketable += 1
        else:
            not_bracketable += 1

    rows.sort(key=lambda r: r[0])
    tiers = {
        'le1.005': 0, 'le1.010': 0, 'le1.020': 0, 'le1.050': 0, 'lt1.000': 0,
    }
    for total, *_ in rows:
        if total <= 1.005:
            tiers['le1.005'] += 1
        if total <= 1.010:
            tiers['le1.010'] += 1
        if total <= 1.020:
            tiers['le1.020'] += 1
        if total <= 1.050:
            tiers['le1.050'] += 1
        if total < 1.000:
            tiers['lt1.000'] += 1

    floor = rows[0][0] if rows else None
    leader = rows[0] if rows else None
    return {
        'floor_min_ask': floor,
        'leader': leader,
        'top25': rows[:25],
        'two_sided': two_sided,
        'yes_only': yes_only,
        'na_only': na_only,
        'not_bracketable': not_bracketable,
        'tiers': tiers,
        'n_markets': len(markets),
    }


result = asyncio.run(scan())
print(f"floor_min_ask={result['floor_min_ask']}")
print(f"two_sided={result['two_sided']} yes_only={result['yes_only']} na_only={result['na_only']} not_bracketable={result['not_bracketable']} ({result['not_bracketable']/result['n_markets']*100:.1f}%)")
print(f"tiers={result['tiers']}")
le = result['leader']
print(f"leader: {le[1]} | sum={le[0]:.3f} Y{le[2]:.3f} N{le[3]:.3f} liq={le[4]}")
print("top25:")
for total, q, yp, np_, liq in result['top25']:
    print(f"  {total:.4f} | Y{yp:.3f} N{np_:.3f} | liq={liq} | {q}")

with open('runs/_tmp_cron_20261015T2147Z_supp_rows.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)
