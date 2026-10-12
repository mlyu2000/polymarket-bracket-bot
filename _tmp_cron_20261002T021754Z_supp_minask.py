# Supplement for cron run 2026-10-02T02:18Z.
# Mechanism-agnostic best-ask (min) floor over live books — asks[0] is the WORST
# ask on the CLOB (DESC sort), so the provided near-miss block under-reports.
import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

def best_ask(book):
    return min(float(a['price']) for a in book.asks)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    priced = 0
    brackets = []
    near = []
    det_extra = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = best_ask(yes_book)
        np = best_ask(no_book)
        total = yp + np
        priced += 1
        if total < 1.0:
            brackets.append((total, m.question[:60], yp, np, m.liquidity))
        elif total <= 1.005:
            near.append((total, m.question[:60], yp, np, m.liquidity))
        opp = detector.detect(m, yes_book, no_book)
        if opp and total >= 1.0:
            det_extra.append((opp.total_cost, m.question[:60]))
    brackets.sort()
    near.sort()
    print(f"best-ask scan: {priced}/{len(markets)} markets have two-sided asks ({dt:.1f}s)")
    print(f"BRACKETS (best-ask sum < 1.00): {len(brackets)}")
    for t, q, yp, np, liq in brackets[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"NEAR (1.00 <= sum <= 1.005): {len(near)}")
    for t, q, yp, np, liq in near[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    if det_extra:
        print(f"DETECTOR-ONLY opps (min-sum>=1.0 but detector fired, e.g. fee/gate logic): {len(det_extra)}")
        for t, q in det_extra[:10]:
            print(f"  sum={t:.4f} | {q}")

asyncio.run(scan())
