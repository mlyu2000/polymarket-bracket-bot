import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    out = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            ya = min(float(a['price']) for a in yes_book.asks)
            na = min(float(a['price']) for a in no_book.asks)
            out.append((ya + na, m.question[:55], ya, na, m.liquidity))
    out.sort()
    print(f"best-ask supplement: {len(markets)} markets, {priced} priced, in {time.time()-t0:.1f}s")
    for total, q, yp, np_, liq in out[:8]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"  count sum<1.00: {sum(1 for t,*_ in out if t < 1.00)}")
    print(f"  count sum<=1.005: {sum(1 for t,*_ in out if t <= 1.005)}")
    print(f"  count sum<=1.01: {sum(1 for t,*_ in out if t <= 1.01)}")

asyncio.run(scan())
