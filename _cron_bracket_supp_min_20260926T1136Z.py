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

    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            totals.append((yp + np_, m.question[:55], yp, np_, m.liquidity))

    totals.sort()
    brackets = [t for t in totals if t[0] < 1.0]
    near = [t for t in totals if 1.0 <= t[0] <= 1.005]
    print(f"MIN-ASK SCAN: {len(markets)} markets priced in {scan_time:.1f}s ({len(totals)} with both books)")
    print(f"TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for total, q, yp, np_, liq in brackets[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"NEAR (1.000-1.005): {len(near)}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print("GLOBAL TOP-10 LOWEST SUMS:")
    for total, q, yp, np_, liq in totals[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")

asyncio.run(scan())
