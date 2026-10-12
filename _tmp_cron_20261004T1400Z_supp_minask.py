import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            sums.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    sums.sort()
    print(f"Markets with both books: {len(sums)} in {scan_time:.1f}s")
    priced = [s for s in sums if s[0] > 0.02]
    print(f"True floor (min-ask sum): {priced[0][0]:.3f} | {priced[0][1]}" if priced else "no priced")
    print("Top-10 lowest min-ask sums:")
    for total, q, yp, np_, liq in sums[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    lt1005 = [s for s in sums if s[0] <= 1.005]
    lt100 = [s for s in sums if s[0] < 1.0]
    print(f"min-ask sums <=1.005: {len(lt1005)}  |  <1.00: {len(lt100)}")
    for total, q, yp, np_, liq in lt1005[:10]:
        flag = "BRACKET-CANDIDATE" if total < 1.0 else ""
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q} {flag}")

asyncio.run(scan())
