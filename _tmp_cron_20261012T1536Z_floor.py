"""Floor supplement for 20261012T1536Z scan: lowest 2-sided min-ask sums."""
import asyncio
import logging

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
        if not (yb and nb and yb.asks and nb.asks):
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    return rows


rows = asyncio.run(scan())
print(f"FLOOR scan: {len(rows)} two-sided priced markets")
print("Lowest 8 min-ask sums:")
for total, q, yp, np_, liq in rows[:8]:
    print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | {q}")
