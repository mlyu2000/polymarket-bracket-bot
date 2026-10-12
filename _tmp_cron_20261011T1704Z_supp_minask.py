"""Supplementary TRUE-FLOOR scan: uses min(all asks) on both books (asks are DESC-sorted,
so asks[0] is the WORST ask and produces a false floor). Persists JSON for run history."""
import asyncio, json, time
from config import Config
from polymarket_api import PolymarketAPI

async def main():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, all_books):
        y_asks = yb.asks if yb else []
        n_asks = nb.asks if nb else []
        if y_asks and n_asks:
            two_sided += 1
        elif y_asks:
            yes_only += 1
        elif n_asks:
            no_only += 1
        else:
            empty += 1
        if not (y_asks and n_asks):
            continue
        yp = min(float(a['price']) for a in y_asks)
        npp = min(float(a['price']) for a in n_asks)
        rows.append({'total': yp + npp, 'q': m.question, 'yes': yp, 'no': npp,
                     'liq': m.liquidity, 'yes_depth': sum(float(a['size']) for a in y_asks),
                     'no_depth': sum(float(a['size']) for a in n_asks)})

    rows.sort(key=lambda r: r['total'])
    band = [r for r in rows if r['total'] <= 1.005]
    tier = [r for r in rows if r['total'] <= 1.02]

    print(f"TRUE FLOOR: {rows[0]['total']:.4f}" if rows else "no two-sided books")
    print(f"band<=1.005 n={len(band)}:")
    for r in band[:5]:
        print(f"  {r['total']:.4f} | Y@{r['yes']:.3f} N@{r['no']:.3f} | liq={r['liq']} | {r['q'][:60]}")
    print(f"tier<=1.020 n={len(tier)}:")
    for r in tier[:5]:
        print(f"  {r['total']:.4f} | Y@{r['yes']:.3f} N@{r['no']:.3f} | liq={r['liq']} | {r['q'][:60]}")
    print(f"books: two_sided={two_sided} yes_only={yes_only} no_only={no_only} empty={empty} total={len(markets)}")
    print(f"scan_time={scan_time:.1f}s")

    out = {'floor': rows[0]['total'] if rows else None,
           'band_le_1_005': band[:10], 'tier_le_1_02': tier[:10],
           'two_sided': two_sided, 'yes_only': yes_only, 'no_only': no_only, 'empty': empty,
           'markets': len(markets), 'scan_time': scan_time,
           'bottom20': rows[:20]}
    with open('_tmp_cron_20261011T1704Z_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)

asyncio.run(main())
