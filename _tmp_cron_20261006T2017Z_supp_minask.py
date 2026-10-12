import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    def best_ask(book):
        return min((float(a['price']) for a in book.asks), default=None)

    rows = []
    skipped = 0
    det_opps = 0
    for m, (yb, nb) in zip(markets, all_books):
        opp = detector.detect(m, yb, nb)
        if opp:
            det_opps += 1
        if not yb or not nb or not yb.asks or not nb.asks:
            skipped += 1
            continue
        yp = best_ask(yb)
        np_ = best_ask(nb)
        if yp is None or np_ is None or yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            skipped += 1
            continue
        total = yp + np_
        rows.append((total, m.question[:55], yp, np_, m.liquidity))

    rows.sort()
    print(f"[min-ask ground truth] {len(markets)} markets, {len(rows)} priced, {skipped} skipped, {dt:.1f}s")
    print(f"[detector-opps cross-check] {det_opps}")
    nm = [r for r in rows if r[0] <= 1.005]
    lt1 = [r for r in rows if r[0] < 1.0]
    print(f"sum<1.00: {len(lt1)} | sum<=1.005: {len(nm)}")
    print("--- 10 lowest best-ask sums ---")
    for t, q, yp, np_, liq in rows[:10]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq=${liq:,.0f} | {q}")
    print("--- gross sum<1.00 markets (any liquidity) ---")
    for t, q, yp, np_, liq in lt1:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq=${liq:,.0f} | {q}")

asyncio.run(scan())
