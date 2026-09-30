import asyncio, logging
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from config import Config

logging.basicConfig(level=logging.ERROR)

async def main():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a["price"]) for a in yb.asks)
        na = min(float(a["price"]) for a in nb.asks)
        rows.append((ya + na, m.question[:60], ya, na, m.liquidity, m.volume24hr if hasattr(m, "volume24hr") else m.volume))
    rows.sort()
    print("priced", len(rows))
    if rows:
        print("floor", f"{rows[0][0]:.4f}", rows[0][1])
    b = [r for r in rows if r[0] < 1.0]
    print("brackets", len(b))
    for r in b[:10]:
        print("  ", f"{r[0]:.4f}", f"Y@{r[2]:.3f}", f"N@{r[3]:.3f}", "liq", r[4], "vol", r[5], "|", r[1])
    nm = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print("near_1.000_1.005", len(nm))
    for r in nm[:10]:
        print("  ", f"{r[0]:.4f}", f"Y@{r[2]:.3f}", f"N@{r[3]:.3f}", "liq", r[4], "vol", r[5], "|", r[1])
    print("top10")
    for r in rows[:10]:
        print("  ", f"{r[0]:.4f}", f"Y@{r[2]:.3f}", f"N@{r[3]:.3f}", "liq", r[4], "|", r[1])

asyncio.run(main())
