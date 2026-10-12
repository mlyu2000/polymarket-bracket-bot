import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            ya = min(float(a['price']) for a in yb.asks)
            na = min(float(a['price']) for a in nb.asks)
            priced += 1
            rows.append((ya + na, ya, na, m.question[:55], m.liquidity))
    rows.sort()
    print(f"priced_markets={priced}")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"true_brackets_bestask_lt1.000={len(lt1)}")
    for r in lt1[:10]:
        print(f"  SUM={r[0]:.4f} Yes@{r[1]:.3f} No@{r[2]:.3f} liq={r[4]} | {r[3]}")
    print("top6 best-ask sums:")
    for r in rows[:6]:
        print(f"  SUM={r[0]:.4f} Yes@{r[1]:.3f} No@{r[2]:.3f} liq={r[4]} | {r[3]}")

asyncio.run(main())
