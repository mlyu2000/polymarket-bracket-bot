import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book):
            continue
        yasks = [float(a['price']) for a in yes_book.asks]
        nasks = [float(a['price']) for a in no_book.asks]
        if not yasks or not nasks:
            continue
        ymin = min(yasks)
        nmin = min(nasks)
        total = ymin + nmin
        rows.append({
            'q': m.question,
            'yes_min': ymin,
            'no_min': nmin,
            'total': total,
            'liq': m.liquidity,
            'n_yes_asks': len(yasks),
            'n_no_asks': len(nasks),
        })

    rows.sort(key=lambda r: r['total'])
    with open('runs/_tmp_cron_20261012T1520Z_supp_data.json', 'w') as f:
        json.dump(rows, f, indent=2)

    two_sided = sum(1 for r in rows if r['yes_min'] < 0.98 and r['no_min'] < 0.98)
    yes_only = sum(1 for r in rows if r['yes_min'] < 0.98 and r['no_min'] >= 0.98)
    no_only = sum(1 for r in rows if r['yes_min'] >= 0.98 and r['no_min'] < 0.98)
    empty = len(markets) - len(rows)
    print(f"structural: two_sided={two_sided} yes_only={yes_only} no_only={no_only} empty={empty} total={len(markets)}")
    if rows:
        print(f"TRUE FLOOR (min of all asks, two-sided): {rows[0]['total']:.4f}")
        for r in rows[:8]:
            print(f"  {r['total']:.4f} | Yes@{r['yes_min']:.3f} No@{r['no_min']:.3f} | liq={r['liq']:.0f} | {r['q'][:60]}")
    # tier counts
    for thr in (1.000, 1.005, 1.010, 1.020, 1.030):
        print(f"  <= {thr:.3f}: {sum(1 for r in rows if r['total'] <= thr)}")
    if len(rows) > 1:
        med = rows[len(rows)//2]['total']
        print(f"median total (two-sided rows): {med:.4f} (n={len(rows)})")

asyncio.run(supp())
