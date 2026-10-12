# Supplementary: true min-ask near-misses (verbatim block uses asks[0] = worst ask
# because CLOB /book returns asks DESC-sorted, so it structurally finds none).
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
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
    rows.sort()
    print(f"min-ask floor scan: {len(rows)} priced markets")
    print("BEST 5 (true min asks):")
    for t, q, yp, np_, liq in rows[:5]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    nm = [r for r in rows if r[0] <= 1.005]
    print(f"near-misses (<=1.005): {len(nm)}")
    for t, q, yp, np_, liq in nm[:10]:
        print(f"  {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
