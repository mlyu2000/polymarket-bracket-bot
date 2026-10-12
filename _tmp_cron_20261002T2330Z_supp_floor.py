import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def floor_scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        priced += 1
        ya = min(float(a['price']) for a in yb.asks)
        na = min(float(a['price']) for a in nb.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity))
    rows.sort()
    print(f"Floor scan (best asks): {len(markets)} markets, {priced} priced both sides")
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"sum<1.00 on BEST asks: {len(lt1)}")
    for r in lt1[:10]:
        print(f"  🔴 {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {r[1]}")
    print("Top-10 lowest totals (best asks):")
    for r in rows[:10]:
        print(f"  {r[0]:.4f} | Yes@{r[2]:.3f} No@{r[3]:.3f} | liq={r[4]:.0f} | {r[1]}")

asyncio.run(floor_scan())
