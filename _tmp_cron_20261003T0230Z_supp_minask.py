import asyncio, logging
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
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        t = yp + np_
        priced += 1
        rows.append((t, m.question[:70], yp, np_, m.liquidity))

    rows.sort()
    print(f"best-ask priced markets: {priced}/{len(markets)}")
    print("--- top 10 lowest sum(bestAskYes)+sum(bestAskNo) ---")
    for t, q, yp, np_, liq in rows[:10]:
        flag = " <-- BRACKET" if t < 1.0 else (" <-- near" if t <= 1.005 else "")
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}{flag}")

asyncio.run(main())
