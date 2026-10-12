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

    rows = []
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yb = min(float(a['price']) for a in yes_book.asks)
            nb = min(float(a['price']) for a in no_book.asks)
            total = yb + nb
            if total < 1.0:
                brackets.append((total, m.question[:60], yb, nb, m.liquidity))
            elif total <= 1.005:
                rows.append((total, m.question[:50], yb, nb, m.liquidity))
    brackets.sort()
    rows.sort()
    print(f"best-ask pass: {len(markets)} markets in {scan_time:.1f}s")
    print(f"BEST-ASK BRACKETS (sum<1.00): {len(brackets)}")
    for total, q, yb, nb, liq in brackets:
        print(f"  sum={total:.4f} | Yes@{yb:.3f} No@{nb:.3f} | liq={liq} | {q}")
    print(f"BEST-ASK NEAR-MISSES (<=1.005): {len(rows)}")
    for total, q, yb, nb, liq in rows[:10]:
        print(f"  {total:.4f} | Yes@{yb:.3f} No@{nb:.3f} | liq={liq} | {q}")

asyncio.run(scan())
