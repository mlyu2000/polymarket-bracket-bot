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
    totals = []
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb and yb.asks and nb.asks):
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        totals.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    totals.sort()
    return len(markets), totals

n, totals = asyncio.run(scan())
print(f"priced books: {len(totals)} / {n} markets")
print(f"floor (min best-ask sum): {totals[0][0]:.4f}")
print("10 tightest:")
for t, q, yp, np_, liq in totals[:10]:
    print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
