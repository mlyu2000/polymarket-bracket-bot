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
    both_priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if m.liquidity <= 0:
            continue
        ya = min(yes_book.asks, key=lambda a: float(a["price"]))
        na = min(no_book.asks, key=lambda a: float(a["price"]))
        yp = float(ya["price"]); np_ = float(na["price"])
        if yp <= 0 or np_ <= 0 or yp >= 1 or np_ >= 1:
            continue
        both_priced += 1
        total = yp + np_
        rows.append({
            "sum": round(total, 4),
            "q": m.question[:70],
            "yes": yp, "yes_size": int(float(ya["size"])),
            "no": np_, "no_size": int(float(na["size"])),
            "overlap": min(int(float(ya["size"])), int(float(na["size"]))),
            "liq": m.liquidity,
        })
    rows.sort(key=lambda r: r["sum"])
    print(f"both_sides_priced={both_priced}")
    print("TOP-15 min-ask totals:")
    for r in rows[:15]:
        print(f"  {r['sum']:.3f} | yes {r['yes']:.3f} x{r['yes_size']} / no {r['no']:.3f} x{r['no_size']} | ov={r['overlap']} | liq={r['liq']} | {r['q']}")
    brackets = [r for r in rows if r["sum"] < 1.0]
    print(f"true_brackets_min_ask={len(brackets)}")
    for r in brackets:
        print(f"  BRACKET {r['sum']:.4f} | {r['q']}")
    with open("_tmp_cron_20261005T1651Z_supp_data.json", "w") as f:
        json.dump({"both_priced": both_priced, "top": rows[:15]}, f)

asyncio.run(supp())
