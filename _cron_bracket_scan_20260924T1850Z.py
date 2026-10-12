"""Cron run 2026-09-24T18:50Z.

Part A: user-provided scan script verbatim (asks[0] near-misses + paper exec).
Part B: mechanism-agnostic min-ask floor supplement over the SAME books
        (asks[0] on the CLOB /book is the WORST ask - descending sort - so the
        provided near-miss block under-reports; detector.py uses min() and
        is correct).
Persists runs/cron_scan_20260924T1850Z.json for git-persisted runs.
"""
import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    paper_results = []
    near_misses = []      # provided method: asks[0]
    minask_near = []      # supplement: min-price ask
    priced = 0
    best_min_sum = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
            paper_results.append(paper.execute(opp))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                yes_price = float(yes_book.asks[0]['price'])
                no_price = float(no_book.asks[0]['price'])
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

        # Part B over the same books
        if yes_book and no_book and yes_book.asks and no_book.asks:
            priced += 1
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            tot = yp + np_
            if best_min_sum is None or tot < best_min_sum[0]:
                best_min_sum = (tot, m.question[:60], yp, np_)
            if tot <= 1.005:
                minask_near.append((tot, m.question[:60], yp, np_, m.liquidity))

    near_misses.sort()
    minask_near.sort()
    print(f"🔍 Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ BRACKETS (sum < 1.00): {len(opps)}")
    for o in opps:
        print(f"  🔴 {o['sum']:.3f} (edge={o['edge']:.4f}) | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']} shares | liq={o['liq']} | {o['q']}")
    print(f"📊 Near-misses (≤1.005, asks[0] method): {len(near_misses)}")
    for total, q, yp, np_, liq in near_misses[:5]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
    print(f"--- Part B: best-ask (min) supplement over {priced} priced markets ---")
    print(f"best-ask near-misses (≤1.005): {len(minask_near)}")
    for tot, q, yp, np_, liq in minask_near[:10]:
        print(f"  {tot:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    if best_min_sum:
        print(f"global min-ask floor: {best_min_sum[0]:.3f} | Yes@{best_min_sum[2]:.3f} No@{best_min_sum[3]:.3f} | {best_min_sum[1]}")

    out = {
        "ts": "2026-09-24T1850Z",
        "markets": len(markets),
        "priced": priced,
        "scan_time_s": round(scan_time, 1),
        "brackets": opps,
        "paper_executions": [str(r) for r in paper_results],
        "near_misses_asks0": near_misses,
        "near_misses_bestask": minask_near,
        "min_floor_bestask": list(best_min_sum) if best_min_sum else None,
    }
    with open("runs/cron_scan_20260924T1850Z.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"[saved runs/cron_scan_20260924T1850Z.json]")

asyncio.run(scan())
