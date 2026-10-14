import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    two_sided = 0
    yes_only = 0
    no_book_missing = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb:
            no_book_missing += 1
            continue
        y_asks = [float(a['price']) for a in (yb.asks or [])]
        n_asks = [float(a['price']) for a in (nb.asks or [])]
        if not y_asks or not n_asks:
            yes_only += 1
            continue
        two_sided += 1
        ymin, nmin = min(y_asks), min(n_asks)
        rows.append({
            'q': m.question,
            'sum': round(ymin + nmin, 4),
            'yes': ymin,
            'no': nmin,
            'liq': m.liquidity,
            'y_asks': len(y_asks),
            'n_asks': len(n_asks),
            'spread': round(abs(ymin - nmin), 4),
        })

    rows.sort(key=lambda r: r['sum'])
    tiers = {}
    for thr in (1.010, 1.020, 1.050, 1.100):
        tiers[str(thr)] = sum(1 for r in rows if r['sum'] <= thr)

    print(f"🔍 Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"two-sided: {two_sided} | ask-only(one side empty): {yes_only} | missing book: {no_book_missing}")
    print(f"Tier counts (min-ask sum <=): " + ", ".join(f"{k}->{v}" for k, v in tiers.items()))
    print(f"True min-ask floor: {rows[0]['sum']:.4f} | {rows[0]['q'][:70]}")
    print(f"  Yes@{rows[0]['yes']:.3f} No@{rows[0]['no']:.3f} liq={rows[0]['liq']} yasks={rows[0]['y_asks']} nasks={rows[0]['n_asks']}")
    print("Top 12 by min-ask sum:")
    for r in rows[:12]:
        print(f"  {r['sum']:.4f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | spread={r['spread']:.3f} | liq={r['liq']} | {r['q'][:60]}")

    with open('tmp_cron_20261014T0517Z_supp_data.json', 'w') as f:
        json.dump({
            'ts': '2026-10-14T05:17Z',
            'markets': len(markets),
            'scan_time': round(scan_time, 1),
            'two_sided': two_sided,
            'ask_only': yes_only,
            'missing_book': no_book_missing,
            'tiers': tiers,
            'floor': rows[0]['sum'],
            'floor_market': rows[0]['q'],
            'top12': rows[:12],
        }, f, indent=2)
    print("saved tmp_cron_20261014T0517Z_supp_data.json")

asyncio.run(scan())
