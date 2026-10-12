"""Supplemental: near-misses computed with MIN ask (asks[0] in /book is DESC-sorted worst ask)."""
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    near = []
    below1 = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if total < 1.0:
                below1.append((total, m.question[:60], yp, np_, m.liquidity))
            elif total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity))
    near.sort()
    below1.sort()
    print(f"Markets with two-sided asks: {priced}/{len(markets)}")
    print(f"TRUE sum<1.00 (min-ask): {len(below1)}")
    for t, q, yp, np_, liq in below1[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq=${liq:,.0f} | {q}")
    print(f"Near-misses (1.000..1.005): {len(near)}")
    for t, q, yp, np_, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq=${liq:,.0f} | {q}")
    if near or below1:
        floor = min(x[0] for x in near + below1)
        print(f"Floor sum observed: {floor:.4f}")

asyncio.run(scan())
