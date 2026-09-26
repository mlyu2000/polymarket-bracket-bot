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
    scan_time = time.time() - t0

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        sums.append((yp + np_, m.question[:55], yp, np_, m.liquidity))
    sums.sort()
    print(f"min-ask scan: {len(markets)} markets in {scan_time:.1f}s | priced: {len(sums)}")
    lt1 = [s for s in sums if s[0] < 1.0]
    le1005 = [s for s in sums if s[0] <= 1.005]
    print(f"sum < 1.000: {len(lt1)} | sum <= 1.005: {len(le1005)}")
    for total, q, yp, np_, liq in sums[:8]:
        print(f"  {total:.3f} | Y@{yp:.3f} N@{np_:.3f} | liq={liq:.0f} | {q}")

asyncio.run(scan())
