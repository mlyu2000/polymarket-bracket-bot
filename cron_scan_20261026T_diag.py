import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    dt = time.time() - t0

    min_total = 10.0
    floor_count_le_1005 = 0
    floor_count_le_100 = 0
    floors = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        if m.liquidity <= 0:
            continue
        y = min(float(a['price']) for a in yes_book.asks)
        n = min(float(a['price']) for a in no_book.asks)
        t = y + n
        if t < min_total:
            min_total = t
        if t <= 1.005:
            floor_count_le_1005 += 1
        if t <= 1.00:
            floor_count_le_100 += 1
        if t <= 1.005:
            floors.append((t, m.question[:45], y, n, m.liquidity))

    floors.sort()
    print(f"📡 Scan: {len(markets)} markets in {dt:.1f}s, {len(floors)} with min-ask sum ≤ 1.005")
    print(f"🔻 Min sum observed: {min_total:.4f}")
    print(f"📊 Near-floor (≤1.005): {floor_count_le_1005}  | (≤1.000): {floor_count_le_100}")
    print("--- tightest 10 (min-ask) ---")
    for t, q, y, n, liq in floors[:10]:
        print(f"  {t:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq:.0f} | {q}")

asyncio.run(main())
