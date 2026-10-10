import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    onesided = 0
    bothempty = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb is None or nb is None:
            continue
        ya = bool(yb.asks)
        na = bool(nb.asks)
        if ya and na:
            priced += 1
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
        elif ya or na:
            onesided += 1
        else:
            bothempty += 1
    rows.sort()
    return len(markets), priced, onesided, bothempty, rows

markets_n, priced_n, onesided, bothempty, rows = asyncio.run(supp())
print(f"priced markets (both-sided): {priced_n}/{markets_n} | one-sided: {onesided} | both-empty: {bothempty}")
if rows:
    print(f"TRUE FLOOR (min-ask sum): {rows[0][0]:.4f} | {rows[0][1]} | Yes@{rows[0][2]:.3f} No@{rows[0][3]:.3f} | liq={rows[0][4]}")
brackets = [r for r in rows if r[0] < 1.0]
band = [r for r in rows if r[0] <= 1.005]
print(f"true brackets (sum<1.00): {len(brackets)}")
for r in brackets:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f}")
print(f"band <=1.005: {len(band)}")
for r in band[:8]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]}")
print("next tier (1.005-1.010):")
for r in [x for x in rows if 1.005 < x[0] <= 1.010][:5]:
    print(f"  {r[0]:.4f} | {r[1]} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]}")
with open('_tmp_cron_20261010T2132Z_supp_data.json', 'w') as f:
    json.dump({'markets': markets_n, 'priced': priced_n, 'onesided': onesided, 'bothempty': bothempty,
               'floor': rows[0][0] if rows else None,
               'floor_q': rows[0][1] if rows else None,
               'brackets': len(brackets),
               'band': [list(r) for r in band]}, f)
