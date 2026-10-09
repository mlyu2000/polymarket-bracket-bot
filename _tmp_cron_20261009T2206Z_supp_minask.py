import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        # TRUE best ask = min price (asks list is DESC-sorted in CLOB payload)
        ya = min(yes_book.asks, key=lambda a: float(a["price"]))
        na = min(no_book.asks, key=lambda a: float(a["price"]))
        yp, np_ = float(ya["price"]), float(na["price"])
        if yp >= 1.0 or np_ >= 1.0 or yp <= 0 or np_ <= 0:
            continue
        rows.append({
            'total': round(yp + np_, 6),
            'q': m.question[:70],
            'yes': yp, 'no': np_,
            'yes_sz': float(ya["size"]), 'no_sz': float(na["size"]),
            'liq': m.liquidity,
        })
    rows.sort(key=lambda r: r['total'])
    with open('_tmp_cron_20261009T2206Z_supp_data.json', 'w') as f:
        json.dump(rows, f, indent=1, default=str)
    print(f"priced markets: {len(rows)}")
    lt1 = [r for r in rows if r['total'] < 1.0]
    le1005 = [r for r in rows if r['total'] <= 1.005]
    print(f"TRUE sum<1.00: {len(lt1)} | sum<=1.005: {len(le1005)}")
    print("--- floor top 10 ---")
    for r in rows[:10]:
        print(f"  {r['total']:.3f} | Y@{r['yes']:.3f} N@{r['no']:.3f} | sz {r['yes_sz']:.0f}/{r['no_sz']:.0f} | liq {r['liq']} | {r['q']}")

asyncio.run(scan())
