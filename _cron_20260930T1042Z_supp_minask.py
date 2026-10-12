import asyncio, logging, json, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    rows = []
    brackets = 0
    for m, (yb, nb) in zip(markets, books):
        if not yb or not nb or not yb.asks or not nb.asks:
            continue
        ya = min(yb.asks, key=lambda a: float(a['price']))
        na = min(nb.asks, key=lambda a: float(a['price']))
        yp, np_ = float(ya['price']), float(na['price'])
        s = yp + np_
        if s < 1.0:
            brackets += 1
        if s <= 1.005:
            rows.append({'sum': round(s, 4), 'yes': yp, 'no': np_,
                         'vol': float(ya.get('size', 0)) + float(na.get('size', 0)),
                         'liq': m.liquidity, 'q': m.question[:60]})
    rows.sort(key=lambda r: r['sum'])
    print(f"SUPP (true best-ask via min): {len(markets)} markets")
    print(f"true sum<1.000: {brackets} | true near-miss <=1.005: {len(rows)}")
    for r in rows[:10]:
        print(f"  {r['sum']:.4f} | Y@{r['yes']:.3f} N@{r['no']:.3f} | askvol={r['vol']:.0f} | liq={r['liq']:.0f} | {r['q']}")
    with open('runs/scan_20260930T1042Z_supp_rows.json', 'w') as f:
        json.dump(rows, f, indent=1)

asyncio.run(main())
