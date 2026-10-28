import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    near_misses = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        if not m.active or m.closed or m.liquidity <= 0:
            continue
        # CORRECT: best ask = min price across ALL ask levels
        yes_price = float(min(yes_book.asks, key=lambda a: float(a["price"]))["price"])
        no_price = float(min(no_book.asks, key=lambda a: float(a["price"]))["price"])
        total = yes_price + no_price
        if total < 1.00:
            brackets.append((total, m.question[:50], yes_price, no_price, m.liquidity))
        elif total <= 1.005:
            near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    brackets.sort()
    print(f"🔍 Scan: {len(markets)} markets in {scan_time:.1f}s")
    print(f"✅ BRACKETS (min-ask, sum < 1.00): {len(brackets)}")
    for total, q, yp, np, liq in brackets[:10]:
        print(f"  🔴 {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")
    print(f"📊 Near-misses (min-ask, ≤1.005): {len(near_misses)}")
    for total, q, yp, np, liq in near_misses[:10]:
        print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq:.0f} | {q}")

asyncio.run(scan())
