import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        rows.append({'sum': round(yp + np_, 4), 'yes': yp, 'no': np_,
                     'q': m.question[:70], 'liq': m.liquidity})

    rows.sort(key=lambda r: r['sum'])
    return rows, len(markets), scan_time

rows, n, dt = asyncio.run(scan())
print(f"corrected-min-ask scan: {n} markets in {dt:.1f}s")
print(f"sum<1.00: {sum(1 for r in rows if r['sum'] < 1.0)}")
print(f"sum<=1.005: {sum(1 for r in rows if r['sum'] <= 1.005)}")
print(f"sum<=1.01: {sum(1 for r in rows if r['sum'] <= 1.01)}")
with open('_tmp_cron_20261007T0800Z_supp_data.json', 'w') as f:
    json.dump(rows, f)
for r in rows[:10]:
    print(f"  {r['sum']:.3f} | Yes@{r['yes']:.3f} No@{r['no']:.3f} | liq={r['liq']} | {r['q']}")
