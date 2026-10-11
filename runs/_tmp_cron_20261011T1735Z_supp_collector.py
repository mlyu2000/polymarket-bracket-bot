"""Cron supplementary-data collector — mirrors detector min-ask pricing.

The cron script's near-miss block uses asks[0], which is the WORST ask on this
CLOB payload (asks are DESC-sorted), so it always reports 0 — a known artifact.
This collector recomputes the floor the way the detector does (min by price).
"""
import asyncio, json, logging, statistics, time
from datetime import datetime, timezone

from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from paper_executor import PaperExecutor

logging.basicConfig(level=logging.ERROR)

TS = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%MZ")


def best_ask(book):
    if not book or not book.asks:
        return None
    a = min(book.asks, key=lambda x: float(x["price"]))
    return float(a["price"])


async def main():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    paper = PaperExecutor()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    brackets = []
    executions = 0
    priced = []          # markets with both books having asks (min-ask sums)
    band = []            # min-ask sum <= 1.005
    two_sided = yes_only = no_only = empty = 0

    for m, (yb, nb) in zip(markets, all_books):
        y_asks = bool(yb and yb.asks)
        n_asks = bool(nb and nb.asks)
        if y_asks and n_asks:
            two_sided += 1
        elif y_asks:
            yes_only += 1
        elif n_asks:
            no_only += 1
        else:
            empty += 1

        opp = detector.detect(m, yb, nb)
        if opp:
            brackets.append({
                "q": m.question, "yes": opp.yes_price, "no": opp.no_price,
                "sum": opp.total_cost, "edge": opp.net_edge,
                "shares": opp.max_shares, "usdc": opp.max_usdc,
            })
            paper.execute(opp)
            executions += 1
            continue

        yp, np_ = best_ask(yb), best_ask(nb)
        if yp is None or np_ is None:
            continue
        total = round(yp + np_, 4)
        entry = (total, m.question[:60], yp, np_, m.liquidity)
        priced.append(entry)
        if total <= 1.005:
            band.append(entry)

    priced.sort()
    band.sort()
    floor = priced[0] if priced else None
    sums = [p[0] for p in priced]

    data = {
        "cron_run_ts": TS,
        "scan": {
            "markets": len(markets),
            "brackets": len(brackets),
            "bracket_details": brackets,
            "detector_opps": len(brackets),
            "executions": executions,
            "scan_time_s": round(scan_time, 1),
            "two_sided_books": two_sided,
            "yes_only": yes_only,
            "no_only": no_only,
            "empty": empty,
            "priced": len(priced),
            "floor": floor[0] if floor else None,
            "floor_leader": {
                "question": floor[1], "yes_ask": floor[2],
                "no_ask": floor[3], "liquidity": floor[4],
            } if floor else None,
            "near_miss_band_le_1005": [
                {"sum": b[0], "q": b[1], "yes": b[2], "no": b[3], "liq": b[4]}
                for b in band
            ],
            "band_count": len(band),
            "top5_closest": [
                {"sum": p[0], "yes": p[2], "no": p[3], "q": p[1]}
                for p in priced[:5]
            ],
            "distribution": {
                "le_1000": sum(1 for s in sums if s < 1.0),
                "le_1005": sum(1 for s in sums if s <= 1.005),
                "le_1010": sum(1 for s in sums if s <= 1.010),
                "le_1050": sum(1 for s in sums if s <= 1.050),
            },
            "median_two_sided_floor": round(statistics.median(sums), 4) if sums else None,
        },
    }
    out = f"runs/_tmp_cron_{TS}_supp_data.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data["scan"], indent=2)[:4000])
    print(f"\nWROTE {out}")


asyncio.run(main())
