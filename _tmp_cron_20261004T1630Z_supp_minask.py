import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    brackets_min = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        ya = min(yes_book.asks, key=lambda a: float(a['price']))
        na = min(no_book.asks, key=lambda a: float(a['price']))
        yp, np_ = float(ya['price']), float(na['price'])
        total = yp + np_
        row = {'sum': total, 'q': m.question[:70], 'yes': yp, 'no': np_,
               'yes_sz': float(ya['size']), 'no_sz': float(na['size']), 'liq': m.liquidity}
        if total < 1.0:
            brackets_min.append(row)
        rows.append(row)

    rows.sort(key=lambda r: r['sum'])
    return {'markets': len(markets), 'priced': len(rows),
            'brackets_min': brackets_min, 'floor': rows[:12]}

res = asyncio.run(scan())
print(f"priced={res['priced']}/{res['markets']}")
print(f"TRUE BRACKETS via min-ask (sum<1.00): {len(res['brackets_min'])}")
for b in res['brackets_min']:
    print(f"  {b['sum']:.4f} | Yes@{b['yes']:.3f}(sz{b['yes_sz']:.0f}) No@{b['no']:.3f}(sz{b['no_sz']:.0f}) | liq={b['liq']} | {b['q']}")
print("Top-12 lowest true totals (floor check):")
for r in res['floor']:
    print(f"  {r['sum']:.4f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
with open('_tmp_cron_20261004T1630Z_supp_data.json','w') as f:
    json.dump(res, f, default=str)
