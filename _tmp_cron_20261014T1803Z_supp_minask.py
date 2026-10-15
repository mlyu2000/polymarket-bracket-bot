import asyncio, json, logging, time, datetime

from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)


async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    two_sided = 0
    not_bracketable = 0
    no_book = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not (yb and nb):
            no_book += 1
            continue
        has_yes = bool(yb.asks)
        has_no = bool(nb.asks)
        if has_yes and has_no:
            two_sided += 1
            min_yes = min(float(a["price"]) for a in yb.asks)
            min_no = min(float(a["price"]) for a in nb.asks)
            total = min_yes + min_no
            rows.append({
                "q": m.question[:80],
                "slug": m.slug,
                "min_yes": min_yes,
                "min_no": min_no,
                "sum": total,
                "liq": m.liquidity,
            })
        else:
            # one leg ask-only (yes-only or no-only book): NO token cannot be
            # acquired via YES bids — not bracketable through this path
            not_bracketable += 1

    rows.sort(key=lambda r: r["sum"])
    tiers = {
        "le1.050": sum(1 for r in rows if r["sum"] <= 1.050),
        "le1.020": sum(1 for r in rows if r["sum"] <= 1.020),
        "le1.010": sum(1 for r in rows if r["sum"] <= 1.010),
        "le1.005": sum(1 for r in rows if r["sum"] <= 1.005),
        "lt1.000": sum(1 for r in rows if r["sum"] < 1.000),
    }
    return {
        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%MZ"),
        "scan_time": round(scan_time, 1),
        "markets": len(markets),
        "two_sided": two_sided,
        "not_bracketable": not_bracketable,
        "no_book": no_book,
        "tiers": tiers,
        "top10": rows[:10],
    }


result = asyncio.run(scan())
print(json.dumps(result, indent=1))
