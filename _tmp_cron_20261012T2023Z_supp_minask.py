import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []       # (min_yes + min_no, question, min_yes, min_no, liquidity)
    two_sided = yes_only = no_only = empty = 0
    best_gross_edge = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        ya = [float(a['price']) for a in (yes_book.asks or [])] if yes_book else []
        na = [float(a['price']) for a in (no_book.asks or [])] if no_book else []
        if ya and na:
            two_sided += 1
            my, mn = min(ya), min(na)
            ge = 1.0 - (my + mn)
            if best_gross_edge is None or ge > best_gross_edge:
                best_gross_edge = ge
            rows.append((my + mn, m.question[:80], my, mn, m.liquidity))
        elif ya:
            yes_only += 1
        elif na:
            no_only += 1
        else:
            empty += 1

    rows.sort()
    tiers = {}
    for t in (1.005, 1.010, 1.020, 1.030, 1.050):
        tiers[f"<={t}"] = sum(1 for r in rows if r[0] <= t)

    med = rows[len(rows)//2][0] if rows else None
    out = {
        'ts_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'n_markets': len(markets),
        'n_two_sided': two_sided,
        'yes_only': yes_only,
        'no_only': no_only,
        'empty': empty,
        'tiers': tiers,
        'floor': rows[0] if rows else None,
        'top10': rows[:10],
        'n_band_1005': sum(1 for r in rows if r[0] <= 1.005),
        'median_minask': med,
        'best_gross_edge': best_gross_edge,
    }
    with open('runs/_tmp_cron_20261012T2023Z_supp_data.json', 'w') as f:
        json.dump(out, f, indent=1, default=str)

    print(f"two_sided={two_sided} yes_only={yes_only} no_only={no_only} empty={empty}")
    print(f"tiers: {tiers}")
    print(f"best_gross_edge: {best_gross_edge}")
    if rows:
        print(f"FLOOR: {rows[0][0]:.4f} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq {rows[0][4]} | {rows[0][1]}")
        print("top10:")
        for total, q, yp, np, liq in rows[:10]:
            print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq {liq} | {q}")
        print(f"band<=1.005 n={out['n_band_1005']}")

asyncio.run(supp())
