import asyncio, json, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)
TS = "20261013T1556Z"

TRACKED_Q = "Will US unemployment reach at least 6.0% in 2026?"
TRACKED_SLUG = "will-us-unemployment-reach-at-least-6pt0-in-2026"


async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    two_sided = yes_only = no_only = empty = 0
    for m, (yb, nb) in zip(markets, books):
        if yb and nb and yb.asks and nb.asks:
            y = min(float(a["price"]) for a in yb.asks)
            n = min(float(a["price"]) for a in nb.asks)
            rows.append({
                "sum": round(y + n, 4), "yes": y, "no": n,
                "n_asks_y": len(yb.asks), "n_asks_n": len(nb.asks),
                "liq": m.liquidity, "q": m.question,
            })
            two_sided += 1
        elif yb and yb.asks:
            yes_only += 1
        elif nb and nb.asks:
            no_only += 1
        else:
            empty += 1

    rows.sort(key=lambda r: r["sum"])
    median = rows[len(rows) // 2]["sum"] if rows else None
    tiers = {
        "le1000": sum(1 for r in rows if r["sum"] <= 1.000),
        "le1005": sum(1 for r in rows if r["sum"] <= 1.005),
        "le1010": sum(1 for r in rows if r["sum"] <= 1.010),
        "le1020": sum(1 for r in rows if r["sum"] <= 1.020),
        "le1030": sum(1 for r in rows if r["sum"] <= 1.030),
        "le1050": sum(1 for r in rows if r["sum"] <= 1.050),
    }

    # --- tracked floor market verification via direct CLOB /book ---
    tracked = None
    try:
        search = await api._request(
            f"{api.gamma_base}/public-search?q=unemployment+6.0%25&limit_per_type=5"
        )
        events = search.get("events") or []
        target = None
        for ev in events:
            for mk in ev.get("markets") or []:
                if TRACKED_SLUG in (mk.get("slug") or ""):
                    target = mk
                    break
            if target:
                break
        if target:
            ids = json.loads(target["clobTokenIds"]) if isinstance(target.get("clobTokenIds"), str) else target.get("clobTokenIds", [])
            yb = await api.fetch_order_book(ids[0])
            nb = await api.fetch_order_book(ids[1])
            y_asks = [float(a["price"]) for a in (yb.asks or [])] if yb else []
            n_asks = [float(a["price"]) for a in (nb.asks or [])] if nb else []
            y_bids = [float(b["price"]) for b in (yb.bids or [])] if yb else []
            tracked = {
                "q": target.get("question", TRACKED_Q),
                "slug": target.get("slug"),
                "active": target.get("active"),
                "closed": target.get("closed"),
                "min_ask": min(y_asks) if y_asks else None,
                "max_bid": max(y_bids) if y_bids else None,
                "n_asks": len(y_asks),
                "n_bids": len(y_bids),
                "no_min_ask": min(n_asks) if n_asks else None,
                "true_floor": round(min(y_asks) + min(n_asks), 4) if y_asks and n_asks else None,
                "liq": target.get("liquidity"),
            }
    except Exception as e:
        tracked = {"error": repr(e)}

    out = {
        "ts": TS,
        "markets": len(markets),
        "scan": "verbatim (asks[0]) + supplementary min-ask",
        "structural": {
            "two_sided": two_sided, "yes_only": yes_only,
            "no_only": no_only, "empty": empty,
        },
        "not_bracketable_pct": round(100 * (len(markets) - two_sided) / len(markets), 1),
        "tiers": tiers,
        "median_two_sided_total": median,
        "floor": rows[0] if rows else None,
        "top12": rows[:12],
        "tracked_floor_market": tracked,
    }
    path = f"runs/_tmp_cron_{TS}_supp_data.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("saved", path)
    print(json.dumps({"floor": rows[0] if rows else None, "tiers": tiers,
                      "median": median, "tracked": tracked}, indent=2))


asyncio.run(main())
