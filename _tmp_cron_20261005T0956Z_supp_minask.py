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

    # Corrected near-miss: best ask = min(asks) since /book asks are DESC-sorted
    near = []
    floors = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append((opp.total_cost, opp.net_edge, opp.max_shares, m.question[:60]))
            continue
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
            np_ = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
            total = yp + np_
            floors.append(total)
            if total <= 1.005:
                near.append((total, m.question[:60], yp, np_, m.liquidity))

    near.sort()
    floors.sort()
    print(f"Markets: {len(markets)}  books fetched in {scan_time:.1f}s")
    print(f"Detector brackets (source-of-truth): {len(brackets)}")
    for b in sorted(brackets):
        print(f"  sum={b[0]:.4f} edge={b[1]:.4f} shares={b[2]} | {b[3]}")
    print(f"CORRECTED near-misses (best-ask sum <= 1.005): {len(near)}")
    for total, q, yp, np_, liq in near[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if floors:
        p05 = floors[max(0, len(floors)//20)]
        print(f"Floor stats over {len(floors)} priced pairs: min={floors[0]:.4f} p05={p05:.4f} median={floors[len(floors)//2]:.4f}")

asyncio.run(scan())
