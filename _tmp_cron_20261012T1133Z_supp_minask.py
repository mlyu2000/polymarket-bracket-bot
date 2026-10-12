import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

TS = "2026-10-12T1133Z"

async def supp():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    priced = 0
    one_sided = 0
    both_empty = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book):
            both_empty += 1
            continue
        yasks = [float(a['price']) for a in yes_book.asks]
        nasks = [float(a['price']) for a in no_book.asks]
        if not yasks or not nasks:
            one_sided += 1
            continue
        priced += 1
        ymin = min(yasks)
        nmin = min(nasks)
        rows.append({
            'q': m.question,
            'yes_min': round(ymin, 4),
            'no_min': round(nmin, 4),
            'total': round(ymin + nmin, 4),
            'liq': round(m.liquidity, 2),
            'n_yes_asks': len(yasks),
            'n_no_asks': len(nasks),
        })

    rows.sort(key=lambda r: r['total'])
    with open(f'runs/_tmp_cron_{TS}_supp_data.json', 'w') as f:
        json.dump({'ts': TS, 'markets': len(markets), 'priced': priced,
                   'one_sided': one_sided, 'both_empty': both_empty,
                   'scan_time': round(scan_time, 1), 'rows': rows}, f, indent=1)

    two_sided = sum(1 for r in rows if r['yes_min'] < 0.98 and r['no_min'] < 0.98)
    yes_only = sum(1 for r in rows if r['yes_min'] < 0.98 and r['no_min'] >= 0.98)
    no_only = sum(1 for r in rows if r['yes_min'] >= 0.98 and r['no_min'] < 0.98)
    empty = len(markets) - len(rows)
    print(f"priced markets: {priced}/{len(markets)} | one-sided: {one_sided} | both-empty: {both_empty} | scan {scan_time:.1f}s")
    print(f"structural: two_sided={two_sided} yes_only={yes_only} no_only={no_only} empty={empty} total={len(markets)}")
    if rows:
        print(f"TRUE FLOOR (min of all asks, both sides priced): {rows[0]['total']:.4f}")
        for r in rows[:10]:
            print(f"  {r['total']:.4f} | Yes@{r['yes_min']:.3f} No@{r['no_min']:.3f} | liq={r['liq']:.0f} | {r['q'][:60]}")
    brackets = [r for r in rows if r['total'] < 1.0]
    band = [r for r in rows if r['total'] <= 1.005]
    print(f"true brackets (sum<1.00): {len(brackets)}")
    for r in brackets:
        print(f"  {r['total']:.4f} | {r['q'][:60]} | Yes@{r['yes_min']:.3f} No@{r['no_min']:.3f}")
    print(f"band <=1.005: {len(band)}")
    for r in band[:6]:
        print(f"  {r['total']:.4f} | {r['q'][:60]} | Yes@{r['yes_min']:.3f} No@{r['no_min']:.3f} | liq={r['liq']:.0f}")
    next_tier = [r for r in rows if 1.005 < r['total'] <= 1.008]
    print(f"tier 1.006-1.008: {len(next_tier)}")
    for r in next_tier[:6]:
        print(f"  {r['total']:.4f} | {r['q'][:60]} | Yes@{r['yes_min']:.3f} No@{r['no_min']:.3f} | liq={r['liq']:.0f}")
    tiers = {
        'le_1005': len(band),
        'le_1010': len([r for r in rows if r['total'] <= 1.010]),
        'le_1020': len([r for r in rows if r['total'] <= 1.020]),
        'le_1030': len([r for r in rows if r['total'] <= 1.030]),
    }
    print(f"tiers: {tiers}")
    actionable = [r for r in rows if r['total'] <= 0.98]
    print(f"actionable (sum<=0.98): {len(actionable)}")
    print("supp data written")

asyncio.run(supp())
