import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    both = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yb = min(yes_book.asks, key=lambda a: float(a['price']))
        nb = min(no_book.asks, key=lambda a: float(a['price']))
        yp, np_ = float(yb['price']), float(nb['price'])
        tot = yp + np_
        ov = min(int(float(yb['size'])), int(float(nb['size'])))
        both += 1
        rows.append({'sum': round(tot, 4), 'q': m.question[:70], 'yes': yp, 'no': np_,
                     'ov': ov, 'liq': m.liquidity})
    rows.sort(key=lambda r: r['sum'])
    print(f"both_sides_priced={both} markets={len(markets)}")
    print(f"min_sum={rows[0]['sum'] if rows else 'n/a'}")
    print("top12 by lowest true best-ask sum:")
    for r in rows[:12]:
        print(f"  {r['sum']:.4f} | Y@{r['yes']:.3f} N@{r['no']:.3f} | ov={r['ov']} liq={r['liq']} | {r['q']}")
    lt1 = [r for r in rows if r['sum'] < 1.0]
    nm = [r for r in rows if r['sum'] <= 1.005]
    print(f"sums_lt_1.0={len(lt1)} sums_le_1.005={len(nm)}")
    with open('_tmp_cron_20261005T1855Z_supp_data.json', 'w') as f:
        json.dump(rows[:30], f, indent=1)

asyncio.run(supp())
