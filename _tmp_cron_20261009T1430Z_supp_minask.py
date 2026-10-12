import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)

    rows = []
    parsed = 0
    empty = 0
    floor = None
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            empty += 1
            continue
        parsed += 1
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        total = yp + np_
        if floor is None or total < floor:
            floor = total
        if total <= 1.005:
            rows.append({'sum': total, 'yes': yp, 'no': np_, 'liq': m.liquidity, 'q': m.question[:70]})
    rows.sort(key=lambda r: r['sum'])
    print(f"best-ask parsed: {parsed}/{len(markets)} (empty books: {empty})")
    print(f"true floor (min sum across priced markets): {floor:.4f}" if floor is not None else "no priced books")
    print(f"near-misses (best-ask sum <= 1.005): {len(rows)}")
    for r in rows[:10]:
        print(f"  {r['sum']:.4f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
    with open('_tmp_cron_20261009T1430Z_supp_data.json', 'w') as f:
        json.dump({'floor': floor, 'rows': rows, 'parsed': parsed, 'empty': empty}, f)

asyncio.run(supp())
