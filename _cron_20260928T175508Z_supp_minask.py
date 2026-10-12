import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    el = time.time() - t0

    rows = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        ya = min(yes_book.asks, key=lambda a: float(a['price']))
        na = min(no_book.asks, key=lambda a: float(a['price']))
        yp, np_ = float(ya['price']), float(na['price'])
        total = yp + np_
        rows.append((total, m.question[:60], yp, np_, m.liquidity,
                     int(float(ya['size'])), int(float(na['size']))))
    rows.sort()
    print(f"⏱ min-ask pass: {len(markets)} markets in {el:.1f}s | priced rows: {len(rows)}")
    print(f"🟢 TRUE BRACKETS best-ask sum<1.00: {sum(1 for r in rows if r[0] < 1.0)}")
    print("💎 Top 10 by lowest sum (true best-ask):")
    for total, q, yp, np_, liq, ys, ns in rows[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq:.0f} | sz {ys}/{ns} | {q}")
    n5 = sum(1 for r in rows if r[0] <= 1.005)
    print(f"📊 Near-misses (sum<=1.005, true best-ask): {n5}")
    print(f"📏 Floor row: {rows[0][0]:.4f}")

asyncio.run(scan())
