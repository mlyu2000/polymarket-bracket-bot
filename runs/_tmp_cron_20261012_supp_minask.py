import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    # TRUE FLOOR: min over ALL asks on each side (asks are DESC-sorted, asks[0] is WORST ~0.999)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        y_min = min((float(a['price']) for a in yb.asks), default=None) if yb and yb.asks else None
        n_min = min((float(a['price']) for a in nb.asks), default=None) if nb and nb.asks else None
        if y_min is not None and n_min is not None:
            rows.append((round(y_min + n_min, 4), m.question[:60], y_min, n_min, m.liquidity))
    rows.sort()

    # STRUCTURAL: classify books (two_sided = both ask sides have real depth)
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        y = bool(yb and yb.asks)
        n = bool(nb and nb.asks)
        if y and n: two_sided += 1
        elif y: yes_only += 1
        elif n: no_only += 1
        else: empty += 1

    # TIERS
    le = lambda t: sum(1 for r in rows if r[0] <= t)

    with open('runs/_tmp_cron_20261012_supp_data.json', 'w') as f:
        json.dump({'floor_rows': rows[:40], 'tiers': {'1.005': le(1.005), '1.010': le(1.010), '1.020': le(1.020), '1.030': le(1.030)}, 'structural': {'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only, 'empty': empty, 'total': len(markets)}}, f)

    print(f"TRUE FLOOR (min-all-asks): {rows[0][0]:.4f}" if rows else "no two-sided books")
    print("--- BAND (sum <= 1.005) ---")
    for r in rows:
        if r[0] <= 1.005:
            print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    print(f"TIERS: <=1.005 n={le(1.005)}, <=1.010 n={le(1.010)}, <=1.020 n={le(1.020)}, <=1.030 n={le(1.030)}")
    print(f"STRUCTURAL: two_sided={two_sided} yes_only={yes_only} no_only={no_only} empty={empty} of {len(markets)}")
    print(f"BEST GROSS EDGE: {rows[0][0]-1.0:.4f}" if rows else "")

asyncio.run(scan())
