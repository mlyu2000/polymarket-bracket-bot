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
    scan_time = time.time() - t0

    priced = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
            no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
            yp = float(yes_ask["price"])
            npr = float(no_ask["price"])
            priced.append((yp + npr, m.question[:60], yp, npr, m.liquidity))

    priced.sort()
    brackets = [p for p in priced if p[0] < 1.0]
    near = [p for p in priced if 1.0 <= p[0] <= 1.005]
    print(f"⏱ min-ask supplement: {len(markets)} markets in {scan_time:.1f}s | {len(priced)} with both asks")
    print(f"🔴 TRUE BRACKETS (min-ask sum < 1.00): {len(brackets)}")
    for total, q, yp, npr, liq in brackets[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
    print(f"📊 min-ask near-misses (1.000–1.005): {len(near)}")
    for total, q, yp, npr, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{npr:.3f} | liq={liq} | {q}")
    if priced:
        print(f"Floor (lowest min-ask sum): {priced[0][0]:.4f} — {priced[0][1]}")

asyncio.run(scan())
