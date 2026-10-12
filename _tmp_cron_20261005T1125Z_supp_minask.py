import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    priced = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(float(a["price"]) for a in yb.asks)
        na = min(float(a["price"]) for a in nb.asks)
        yb_ = max(float(b["price"]) for b in yb.bids) if yb.bids else 0.0
        nb_ = max(float(b["price"]) for b in nb.bids) if nb.bids else 0.0
        spread = (1.0 - (ya + na)) * 100
        rows.append({
            "sum": round(ya + na, 4),
            "yes_ask": ya, "no_ask": na,
            "yes_bid": yb_, "no_bid": nb_,
            "spread_pct": round(spread, 4),
            "liq": m.liquidity,
            "q": m.question[:70],
        })
        priced += 1

    rows.sort(key=lambda r: r["sum"])
    out = {
        "markets": len(markets),
        "priced": priced,
        "true_brackets_lt_1": [r for r in rows if r["sum"] < 1.0],
        "near_1_to_1.005": [r for r in rows if 1.0 <= r["sum"] <= 1.005],
        "top10_lowest": rows[:10],
    }
    print(json.dumps(out, indent=1))

asyncio.run(supp())
