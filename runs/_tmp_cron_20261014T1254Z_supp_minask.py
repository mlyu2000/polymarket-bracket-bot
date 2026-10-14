import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    data = []
    tiers = {'le1000': [], 'le1005': [], 'le1010': [], 'le1020': [], 'le1050': []}
    two_sided = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        two_sided += 1
        ymin = min(float(a['price']) for a in yb.asks)
        nmin = min(float(a['price']) for a in nb.asks)
        total = ymin + nmin
        rec = {'q': m.question[:60], 'y': ymin, 'n': nmin, 't': total, 'liq': m.liquidity}
        data.append(rec)
        if total <= 1.000: tiers['le1000'].append(rec)
        elif total <= 1.005: tiers['le1005'].append(rec)
        elif total <= 1.010: tiers['le1010'].append(rec)
        elif total <= 1.020: tiers['le1020'].append(rec)
        elif total <= 1.050: tiers['le1050'].append(rec)
    data.sort(key=lambda r: r['t'])
    with open('_tmp_cron_20261014T1254Z_supp_data.json', 'w') as f:
        json.dump(data, f, indent=1)
    print(f"mkts={len(markets)} two_sided={two_sided} not_bracketable={len(markets)-two_sided} scan={scan_time:.1f}s")
    for k in ['le1000', 'le1005', 'le1010', 'le1020', 'le1050']:
        print(f"{k}: n={len(tiers[k])}")
    print("--- floor (min all-asks) top 12 ---")
    for r in data[:12]:
        print(f"  {r['t']:.4f} | Y@{r['y']:.3f} N@{r['n']:.3f} | liq ${r['liq']:.0f} | {r['q']}")

asyncio.run(supp())
