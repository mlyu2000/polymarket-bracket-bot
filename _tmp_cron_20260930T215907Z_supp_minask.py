import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        if m.liquidity <= 0:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np, m.question[:60], yp, np, m.liquidity))
    rows.sort()
    print(f"markets with 2-sided books: {len(rows)}")
    n_lt1 = sum(1 for r in rows if r[0] < 1.0)
    n_le1005 = sum(1 for r in rows if r[0] <= 1.005)
    print(f"best-ask sum < 1.00: {n_lt1} | <= 1.005: {n_le1005}")
    for t, q, yp, np, liq in rows[:10]:
        print(f"  {t:.4f} | Y@{yp:.3f} N@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
