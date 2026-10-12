import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            rows.append({'sum': round(ya+na, 4), 'q': m.question[:60], 'yes': ya, 'no': na, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    return rows

rows = asyncio.run(scan())
under = [r for r in rows if r['sum'] < 1.0]
near = [r for r in rows if 1.0 <= r['sum'] <= 1.005]
print(f"priced={len(rows)}")
print(f"sub-1.00 (true brackets, min-ask): {len(under)}")
for r in under[:5]:
    print(f"  {r['sum']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
print(f"near-misses 1.000-1.005 (min-ask): {len(near)}")
for r in near[:5]:
    print(f"  {r['sum']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
