import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            totals.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    totals.sort()
    priced = len(totals)
    print(f"priced pairs: {priced}/{len(markets)}")
    print("best 8 by min-ask sum:")
    for t, q, yp, np_, liq in totals[:8]:
        flag = "BRACKET" if t < 1.0 else "sub-1.01" if t < 1.01 else ""
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q} {flag}")
    lt1 = [t for t,*_ in totals if t < 1.0]
    le1005 = [t for t,*_ in totals if t <= 1.005]
    print(f"sums < 1.00: {len(lt1)} | sums <= 1.005: {len(le1005)}")

asyncio.run(scan())
