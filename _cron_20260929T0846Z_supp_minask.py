import asyncio, logging, time
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
    dt = time.time() - t0
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    rows.sort()
    print(f"Supp(best-ask min) {len(markets)} markets {dt:.1f}s")
    under = [r for r in rows if r[0] < 1.0]
    print(f"sum<1.00 (raw best asks): {len(under)}")
    for r in under[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"near-miss 1.000<sum<=1.005: {len(nm)}")
    for r in nm[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")
    print("top-5 absolute lowest sums:")
    for r in rows[:5]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]} | {r[1]}")

asyncio.run(scan())
