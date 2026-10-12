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
    elapsed = time.time() - t0
    totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            totals.append((yp + np_, m.question[:60], yp, np_, m.liquidity))
    totals.sort()
    print(f"🔍 Supplemental (best-ask via min): {len(markets)} markets in {elapsed:.1f}s; {len(totals)} priced")
    br = [t for t in totals if t[0] < 1.0]
    nm = [t for t in totals if 1.0 <= t[0] <= 1.005]
    print(f"✅ True brackets (sum<1.00): {len(br)}")
    for s, q, yp, np_, liq in br:
        print(f"  🔴 {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"📊 Near-misses 1.000-1.005: {len(nm)}")
    for s, q, yp, np_, liq in nm[:10]:
        print(f"  {s:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if totals:
        print(f"Floor (min sum): {totals[0][0]:.3f} | {totals[0][1]}")

asyncio.run(scan())
