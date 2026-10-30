"""Full scan with persistence in the established runs/_tmp_cron_<TS>Z_supp_data.json format."""
import asyncio, json, time, logging
from collections import Counter
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
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    opps = []
    near_misses = []
    two_sided = 0
    empty_books = 0
    yes_only = 0
    no_only = 0
    not_bracketable = 0
    min_ask_sums = []
    asks0_near = 0

    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            empty_books += 1
            continue
        if not yes_book.asks or not no_book.asks:
            if yes_book.asks and not no_book.asks:
                yes_only += 1
            elif no_book.asks and not yes_book.asks:
                no_only += 1
            else:
                not_bracketable += 1
            continue
        two_sided += 1

        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(yes_ask["price"])
        np = float(no_ask["price"])
        if yp <= 0 or np <= 0 or yp >= 1.0 or np >= 1.0:
            not_bracketable += 1
            continue
        total = yp + np
        min_ask_sums.append(total)

        # asks[0] artifact check (worst ask)
        yp0 = float(yes_book.asks[0]["price"])
        np0 = float(no_book.asks[0]["price"])
        if 0 < yp0 < 1.0 and 0 < np0 < 1.0 and yp0 + np0 <= 1.005:
            asks0_near += 1

        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                "q": m.question[:80],
                "yes": opp.yes_price,
                "no": opp.no_price,
                "sum": opp.total_cost,
                "edge": opp.net_edge,
                "shares": opp.max_shares,
                "liq": m.liquidity
            })
            paper.execute(opp)
        else:
            if total <= 1.005:
                near_misses.append({
                    "total": round(total, 3),
                    "q": m.question[:60],
                    "yes": round(yp, 3),
                    "no": round(np, 3),
                    "liq": m.liquidity
                })

    near_misses.sort(key=lambda x: x["total"])
    min_ask_sums.sort()

    # Balanced near-miss = both sides >= 0.10 (not 0.002/0.997 extremes)
    balanced = [n for n in near_misses if n["yes"] >= 0.10 and n["no"] >= 0.10]

    tiers = {
        "le1.005": sum(1 for t in min_ask_sums if t <= 1.005),
        "le1.010": sum(1 for t in min_ask_sums if t <= 1.010),
        "le1.020": sum(1 for t in min_ask_sums if t <= 1.020),
        "le1.050": sum(1 for t in min_ask_sums if t <= 1.050),
        "lt1.000": sum(1 for t in min_ask_sums if t < 1.000),
    }

    leader = [near_misses[0]["total"], near_misses[0]["q"], near_misses[0]["yes"],
              near_misses[0]["no"], near_misses[0]["liq"]] if near_misses else ["N/A"]

    data = {
        "ts": ts,
        "markets": len(markets),
        "scan_time": round(scan_time, 1),
        "brackets": len(opps),
        "floor_min_ask": round(min_ask_sums[0], 3) if min_ask_sums else None,
        "two_sided": two_sided,
        "not_bracketable": not_bracketable,
        "yes_only": yes_only,
        "no_only": no_only,
        "empty_books": empty_books,
        "near_miss_verbatim_asks0": asks0_near,
        "near_misses_min_le_1.005": len(near_misses),
        "balanced_near_le_1.005": len(balanced),
        "tiers": tiers,
        "leader": leader,
        "top12_min_ask": near_misses[:12],
        "brackets_detail": opps,
        "near_miss_artifact_note": "asks[0] is worst ask (DESC-sorted CLOB /book); verbatim near-miss block always 0; min-ask diag is source of truth"
    }

    fname = f"runs/_tmp_cron_{ts}_supp_data.json"
    with open(fname, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Console summary
    print(f"🔍 Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ BRACKETS (sum < 1.00): {len(opps)}")
    print(f"📊 Two-sided: {two_sided} | empty/no-ask: {empty_books + not_bracketable}")
    print(f"📉 Near-misses (min-ask ≤ 1.005): {len(near_misses)} (balanced: {len(balanced)})")
    print(f"📈 tiers: {tiers}")
    print(f"🐛 asks[0] artifact: {asks0_near}")
    if near_misses:
        print(f"\n📋 Top near-misses:")
        for n in near_misses[:12]:
            print(f"  {n['total']:.3f} | Yes@{n['yes']:.3f} No@{n['no']:.3f} | liq={n['liq']:.0f} | {n['q']}")
    if opps:
        print(f"\n🔴 BRACKETS FOUND:")
        for o in opps:
            print(f"  {o['sum']:.3f} edge={o['edge']:.4f} | Yes@{o['yes']:.3f} No@{o['no']:.3f} | {o['shares']}shares | {o['q']}")

    print(f"\n📁 Persisted: {fname}")
    return data

asyncio.run(scan())
