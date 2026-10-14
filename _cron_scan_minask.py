import asyncio, logging, time
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
    two_sided = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            two_sided += 1
            ymin = min(float(a['price']) for a in yes_book.asks)
            nmin = min(float(a['price']) for a in no_book.asks)
            total = ymin + nmin
            rows.append((total, m.question[:50], ymin, nmin, m.liquidity))
    rows.sort()
    buckets = {'<=1.050':0,'<=1.020':0,'<=1.010':0,'<1.000':0}
    for t,*_ in rows:
        if t < 1.000: buckets['<1.000'] += 1
        if t <= 1.010: buckets['<=1.010'] += 1
        if t <= 1.020: buckets['<=1.020'] += 1
        if t <= 1.050: buckets['<=1.050'] += 1
    print(f"two-sided bookable: {two_sided} / {len(markets)}")
    print(f"true min-ask floor: {rows[0][0]:.4f}  | {rows[0][1]}")
    print(f"buckets: {buckets}")
    print("--- top 12 tightest (min-ask) ---")
    for t,q,yp,np,liq in rows[:12]:
        print(f"  {t:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")

asyncio.run(scan())
