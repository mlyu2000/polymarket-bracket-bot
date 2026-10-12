import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0
    rows = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # asks are DESC-sorted in the CLOB book -> best ask = min()
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(yes_ask["price"]); np_ = float(no_ask["price"])
        rows.append((yp + np_, m.question[:50], yp, np_, m.liquidity))
        priced += 1
    rows.sort()
    print(f"supp minask scan {dt:.1f}s; priced {priced}/{len(markets)}")
    print("floor + band (<=1.005):")
    for t, q, yp, np_, liq in rows:
        if t <= 1.005:
            print(f"  {t:.3f} | yes {yp:.3f} no {np_:.3f} | liq {liq:.0f} | {q}")
    print("next-out (lowest above band):")
    above = [r for r in rows if r[0] > 1.005][:5]
    for t, q, yp, np_, liq in above:
        print(f"  {t:.3f} | yes {yp:.3f} no {np_:.3f} | liq {liq:.0f} | {q}")

asyncio.run(scan())
