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

    brackets = []
    near = []
    two_sided = 0
    yes_only = 0
    empty = 0

    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, m.question[:50], opp.yes_price, opp.no_price))
        if yes_book and no_book and yes_book.asks and no_book.asks:
            two_sided += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            if total <= 1.010:
                near.append((total, m.question[:55], yp, np_, m.liquidity))
        elif (yes_book and yes_book.asks) or (no_book and no_book.asks):
            yes_only += 1
        else:
            empty += 1

    near.sort()
    brackets.sort()
    print(f"Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"Structure: {two_sided} two-sided / {yes_only} yes-only / {empty} empty")
    print(f"BRACKETS (detector, sum < 1.00): {len(brackets)}")
    for b in brackets:
        print(f"  {b[0]:.4f} | Y@{b[2]:.4f} N@{b[3]:.4f} | {b[1]}")
    print(f"Near-misses (min-ask sum <= 1.010): {len(near)}")
    for total, q, yp, np_, liq in near[:25]:
        print(f"  {total:.4f} | Y@{yp:.4f} N@{np_:.4f} | {q} | liq={liq:.0f}")
    if near:
        print(f"True min-ask floor: {near[0][0]:.4f} | {near[0][1]}")

result = asyncio.run(scan())
