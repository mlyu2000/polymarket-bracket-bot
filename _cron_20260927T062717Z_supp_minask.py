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

    true_brackets = []
    near_misses = []
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np = min(float(a['price']) for a in no_book.asks)
        total = yp + np
        floors.append((total, m.question[:50], yp, np, m.liquidity))
        opp = detector.detect(m, yes_book, no_book)
        if opp is None and total < 1.0:
            true_brackets.append((total, m.question[:60], yp, np, m.liquidity))
        elif opp is None and total <= 1.005:
            near_misses.append((total, m.question[:50], yp, np, m.liquidity))

    floors.sort()
    near_misses.sort()
    true_brackets.sort()
    print(f"⏱ min-ask supplement scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"🟢 TRUE BRACKETS (min-ask sum < 1.00): {len(true_brackets)}")
    for total, q, yp, np, liq in true_brackets[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"📊 Near-misses (min-ask sum <= 1.005): {len(near_misses)}")
    for total, q, yp, np, liq in near_misses[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"📉 Global floor: lowest min-ask sums:")
    for total, q, yp, np, liq in floors[:5]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
