"""Supplementary: TRUE floor (min-ask on both sides), two-sided structure, actionable check."""
import asyncio, json, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = []          # two-sided, liq>0, both min-asks < 1.0 -> (total, q, yp, np, liq, ysz, nsz)
    both_empty = 0
    yes_only = 0
    no_only = 0
    two_sided = 0
    floor_markets = []   # two-sided w/o min-ask price guard
    floor_all = []

    for m, (yb, nb) in zip(markets, all_books):
        y_asks = yb.asks if yb else []
        n_asks = nb.asks if nb else []
        if not y_asks and not n_asks:
            both_empty += 1
            continue
        if y_asks and not n_asks:
            yes_only += 1
            continue
        if n_asks and not y_asks:
            no_only += 1
            continue
        two_sided += 1
        if m.liquidity <= 0:
            continue
        yp = min(float(a["price"]) for a in y_asks)
        np_ = min(float(a["price"]) for a in n_asks)
        total = yp + np_
        floor_all.append((total, m.question[:55], yp, np_, m.liquidity))
        if yp < 1.0 and np_ < 1.0:
            ya = min(y_asks, key=lambda a: float(a["price"]))
            na = min(n_asks, key=lambda a: float(a["price"]))
            priced.append((total, m.question[:55], yp, np_, m.liquidity,
                           int(float(ya["size"])), int(float(na["size"]))))

    floor_all.sort()
    priced.sort()
    n = len(floor_all)
    floor = floor_all[0][0] if floor_all else None
    median = floor_all[n // 2][0] if floor_all else None
    actionable = [p for p in priced if p[0] < 0.98]
    band = [p for p in floor_all if p[0] <= 1.005]
    gap = floor - 0.98 if floor is not None else None

    out = {
        "markets": len(markets),
        "two_sided": two_sided, "yes_only": yes_only,
        "no_only": no_only, "both_empty": both_empty,
        "not_bracketable_pct": round((yes_only + no_only + both_empty) / len(markets) * 100, 1),
        "priced": n, "floor": floor, "floor_median": median,
        "gap_to_actionable": round(gap, 4) if gap is not None else None,
        "actionable_lt_0.98": len(actionable),
        "band_le_1.005": [
            {"total": t, "q": q, "yes": yp, "no": np_, "liq": liq}
            for t, q, yp, np_, liq in band
        ],
        "floor5": [
            {"total": t, "q": q, "yes": yp, "no": np_, "liq": liq}
            for t, q, yp, np_, liq in floor_all[:5]
        ],
    }
    with open("_tmp_cron_20261011T1240Z_supp_data.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"markets={len(markets)} two_sided={two_sided} yes_only={yes_only} no_only={no_only} both_empty={both_empty} ({out['not_bracketable_pct']}% not bracket-able)")
    print(f"priced(min-ask both sides, liq>0, <1.0)={n} FLOOR={floor} median={median} gap_to_0.98={out['gap_to_actionable']} actionable(<0.98)={len(actionable)}")
    print("floor5:")
    for t, q, yp, np_, liq in floor_all[:5]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq {liq} | {q}")
    print(f"band<=1.005 n={len(band)}:")
    for t, q, yp, np_, liq in band:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq {liq} | {q}")

asyncio.run(scan())
