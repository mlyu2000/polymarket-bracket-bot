import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            y = min(float(a['price']) for a in yb.asks)
            n = min(float(a['price']) for a in nb.asks)
            rows.append((y + n, y, n, m.question[:60], m.liquidity))
    rows.sort()
    brk = [r for r in rows if r[0] < 1.0]
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"total priced: {len(rows)}")
    print(f"true brackets (<1.00 via min asks): {len(brk)}")
    for r in brk[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[1]:.3f} No@{r[2]:.3f} | liq={r[4]} | {r[3]}")
    print(f"true near-misses (1.000-1.005): {len(nm)}")
    for r in nm[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[1]:.3f} No@{r[2]:.3f} | liq={r[4]} | {r[3]}")
    print(f"overall floor: {rows[0][0]:.4f} | {rows[0][3]}")

asyncio.run(main())
