import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector
from models import Market

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if m.liquidity <= 0:
            continue
        ya = min(yes_book.asks, key=lambda a: float(a['price']))
        na = min(no_book.asks, key=lambda a: float(a['price']))
        yp = float(ya['price']); np_ = float(na['price'])
        if yp <= 0 or np_ <= 0 or yp >= 1.0 or np_ >= 1.0:
            continue
        total = yp + np_
        yv = int(float(ya['size'])); nv = int(float(na['size']))
        depth = min(yv, nv)
        rows.append({'total': round(total, 4), 'q': m.question[:70], 'yes': yp, 'no': np_,
                     'liq': m.liquidity, 'depth': depth})
    rows.sort(key=lambda r: r['total'])
    return rows

rows = asyncio.run(scan())
print(f"Markets with priced books (min-ask): {len(rows)}")
print("Lowest 10 YES+NO totals:")
for r in rows[:10]:
    print(f"  sum={r['total']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | mindepth={r['depth']} | liq={r['liq']:.0f} | {r['q']}")
brackets = [r for r in rows if r['total'] < 1.0]
below_1005 = [r for r in rows if r['total'] <= 1.005]
print(f"min-ask BRACKETS (sum<1.00): {len(brackets)}")
for r in brackets[:10]:
    print(f"  sum={r['total']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | mindepth={r['depth']} | liq={r['liq']:.0f} | {r['q']}")
print(f"min-ask near-misses (≤1.005): {len(below_1005)}")
with open('runs/scan_20260926T1431Z_minask.json', 'w') as f:
    json.dump({'floor_rows_top10': rows[:10], 'brackets': brackets, 'near_1005': below_1005}, f, indent=2, default=str)
