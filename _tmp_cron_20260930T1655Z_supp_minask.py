import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    rows = []
    for m, (yb, nb) in zip(markets, all_books):
        if yb and nb and yb.asks and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            rows.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    rows.sort()
    print(f"Markets with priced books: {len(rows)}")
    print("Top 10 by min-ask sum:")
    for s, q, yp, np_, liq in rows[:10]:
        flag = " <-- BRACKET" if s < 1.0 else (" (near-miss <=1.005)" if s <= 1.005 else "")
        print(f"  sum={s:.3f} Yes@{yp:.3f} No@{np_:.3f} liq={liq} | {q}{flag}")

asyncio.run(supp())
