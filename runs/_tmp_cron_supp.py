"""Cron supplementary pass: corrected min-ask floor stats + tracked-market verification.

Local ops script (unpushed). Persists supporting data to runs/_tmp_cron_<TS>Z_supp_data.json
"""
import asyncio, json, os, time
from datetime import datetime, timezone

import httpx

from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

TS = datetime.now(timezone.utc).strftime("%Y%m%dT%H%MZ")


def best_ask(book):
    if not book or not book.asks:
        return None
    a = min(book.asks, key=lambda x: float(x["price"]))
    return float(a["price"]), int(float(a["size"])), len(book.asks)


async def main():
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    opps = []
    for m, (yb, nb) in zip(markets, books):
        ya = best_ask(yb)
        na = best_ask(nb)
        opp = detector.detect(m, yb, nb)
        if opp:
            opps.append({"q": m.question, "sum": opp.total_cost, "edge": opp.net_edge,
                         "shares": opp.max_shares, "liq": m.liquidity})
        if ya and na:
            total = ya[0] + na[0]
            rows.append({
                "q": m.question, "yes": ya[0], "no": na[0], "sum": total,
                "y_depth": ya[1], "n_depth": na[1],
                "y_levels": ya[2], "n_levels": na[2], "liq": m.liquidity,
                "active": m.active, "closed": m.closed,
            })

    rows.sort(key=lambda r: r["sum"])
    two_sided = [r for r in rows if r["y_levels"] > 0 and r["n_levels"] > 0]
    med = None
    if rows:
        n = len(rows)
        med = rows[n // 2]["sum"] if n % 2 else (rows[n // 2 - 1]["sum"] + rows[n // 2]["sum"]) / 2

    bands = {}
    for thr in (1.000, 1.005, 1.010, 1.020, 1.030, 1.050):
        bands[f"<={thr:.3f}"] = sum(1 for r in rows if r["sum"] <= thr)

    # Structural: how many have a real 2-sided book (bracketable) vs one-sided
    no_book_only = sum(1 for r in rows if r["y_levels"] > 0 and r["n_levels"] == 0)
    yes_book_only = sum(1 for r in rows if r["n_levels"] > 0 and r["y_levels"] == 0)
    fully_two_sided = sum(1 for r in rows if r["y_levels"] > 0 and r["n_levels"] > 0)

    print(f"🔍 Corrected scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ BRACKETS (detector, min-ask, net_edge>=margin): {len(opps)}")
    for o in opps:
        print(f"  🔴 {o['sum']:.4f} edge={o['edge']:.4f} {o['shares']}sh liq={o['liq']:.0f} | {o['q'][:60]}")
    print(f"📊 min-ask floor stats over {len(rows)} priced markets")
    print(f"   median 2-sided min-ask sum: {med:.4f}" if med else "   median: n/a")
    for k, v in bands.items():
        print(f"   sum {k}: {v}")
    print(f"🧱 structure: 2-sided books={fully_two_sided} | yes-asks only={yes_book_only} | no-asks only={no_book_only}")
    print(f"   bracketable share: {fully_two_sided}/{len(rows)} = {100*fully_two_sided/max(len(rows),1):.1f}%")
    print("📉 10 lowest min-ask sums:")
    for r in rows[:10]:
        print(f"   {r['sum']:.4f} | Y@{r['yes']:.4f}({r['y_depth']}sh/{r['y_levels']}lv) "
              f"N@{r['no']:.4f}({r['n_depth']}sh/{r['n_levels']}lv) | {r['q'][:48]}")

    # --- Verify long-tracked floor market directly via CLOB /book ---
    tracked = "will-us-unemployment-reach-at-least-6pt0-in-2026"
    found = None
    async with httpx.AsyncClient(timeout=20) as c:
        try:
            s = await c.get("https://gamma-api.polymarket.com/public-search",
                            params={"q": "unemployment reach at least 6", "limit_per_type": 10})
            s.raise_for_status()
            data = s.json()
            for ev in data.get("events", []):
                for mk in ev.get("markets", []):
                    if "unemployment" in (mk.get("question") or "").lower():
                        found = mk
                        break
                if found:
                    break
        except Exception as e:
            print(f"⚠️ gamma search failed: {e}")

    tracked_info = None
    if found:
        ids = json.loads(found.get("clobTokenIds", "[]"))
        print(f"🎯 Tracked market found: {found.get('question')}")
        print(f"   active={found.get('active')} closed={found.get('closed')} "
              f"archived={found.get('archived')} accepting={found.get('accepting_orders')}")
        print(f"   outcomePrices={found.get('outcomePrices')} liquidity={found.get('liquidity')}")
        print(f"   clobTokenIds={ids}")
        async with httpx.AsyncClient(timeout=20) as c:
            for label, tid in zip(("YES", "NO"), ids[:2]):
                try:
                    r = await c.get(f"https://clob.polymarket.com/book",
                                    params={"token_id": tid})
                    r.raise_for_status()
                    b = r.json()
                    asks = [(float(a["price"]), float(a["size"])) for a in b.get("asks", [])]
                    bids = [(float(x["price"]), float(x["size"])) for x in b.get("bids", [])]
                    asks_sorted = sorted(asks)
                    print(f"   {label} book: {len(asks)} asks / {len(bids)} bids | "
                          f"min-ask={asks_sorted[0] if asks_sorted else None} | "
                          f"max-bid={max(bids) if bids else None}")
                except Exception as e:
                    print(f"   {label} book fetch failed: {e}")
        tracked_info = {
            "question": found.get("question"),
            "active": found.get("active"), "closed": found.get("closed"),
            "archived": found.get("archived"),
            "accepting_orders": found.get("accepting_orders"),
            "outcomePrices": found.get("outcomePrices"),
            "liquidity": found.get("liquidity"),
            "clobTokenIds": ids,
        }
    else:
        print("🎯 Tracked unemployment market NOT found in gamma public-search results")

    out = os.path.join("runs", f"_tmp_cron_{TS}_supp_data.json")
    with open(out, "w") as f:
        json.dump({"ts": TS, "scan_time": scan_time, "n_markets": len(markets),
                   "opps": opps, "rows": rows, "bands": bands,
                   "median_sum": med,
                   "structure": {"two_sided": fully_two_sided, "yes_only": yes_book_only,
                                 "no_only": no_book_only, "priced": len(rows)},
                   "tracked": tracked_info}, f, indent=2, default=str)
    print(f"💾 persisted: {out}")


asyncio.run(main())
