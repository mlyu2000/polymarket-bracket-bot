import asyncio, json, logging, os, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)
TS = os.environ["CRON_TS"]


async def scan():
    Config.validate()
    api = PolymarketAPI()
    mk = await api.fetch_active_markets()
    tp = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in mk]
    books = await api.fetch_order_books_batch(tp)
    rows = []
    for m, (yb, nb) in zip(mk, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        yp = min(float(a["price"]) for a in yb.asks)
        np_ = min(float(a["price"]) for a in nb.asks)
        rows.append(
            {
                "sum": round(yp + np_, 4),
                "yes": yp,
                "no": np_,
                "n_asks_y": len(yb.asks),
                "n_asks_n": len(nb.asks),
                "liq": m.liquidity,
                "q": m.question,
            }
        )
    rows.sort(key=lambda r: r["sum"])
    out = {
        "ts_utc": TS,
        "markets": len(mk),
        "two_sided": len(rows),
        "median_two_sided": rows[len(rows) // 2]["sum"],
        "bands": {
            "le_1.005": sum(1 for r in rows if r["sum"] <= 1.005),
            "le_1.010": sum(1 for r in rows if r["sum"] <= 1.010),
            "le_1.020": sum(1 for r in rows if r["sum"] <= 1.020),
            "le_1.030": sum(1 for r in rows if r["sum"] <= 1.030),
        },
        "floor": rows[0],
        "top12": rows[:12],
    }
    path = "_cron_%s_supp_data.json" % TS
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("saved", path)


asyncio.run(scan())
