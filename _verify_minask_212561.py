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
    elapsed = time.time() - t0
    # True min-ask: best (lowest) ask on each side
    real_near = []
    asks0_near = []
    two_sided = 0
    yes_only = 0
    no_only = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        y_has = yes_book and yes_book.asks
        n_has = no_book and no_book.asks
        if not y_has or not n_has:
            if y_has:
                yes_only += 1
            elif n_has:
                no_only += 1
            continue
        two_sided += 1
        min_yes = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
        min_no = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
        total_min = min_yes + min_no
        if total_min <= 1.005:
            real_near.append((total_min, m.question[:60], min_yes, min_no, m.liquidity))
        # asks[0] version (artifact)
        a0_yes = float(yes_book.asks[0]['price'])
        a0_no = float(no_book.asks[0]['price'])
        if (a0_yes + a0_no) <= 1.005:
            asks0_near.append((a0_yes + a0_no, m.question[:60], a0_yes, a0_no))
    real_near.sort()
    asks0_near.sort()
    print(f"⏱  {len(markets)} markets / {len(all_books)} books in {elapsed:.1f}s")
    print(f"📚 Two-sided books: {two_sided} | yes_only: {yes_only} | no_only: {no_only}")
    print(f"📐 MIN-ASK near-misses (<=1.005): {len(real_near)}")
    for total, q, yp, np, liq in real_near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | {q} | liq={liq}")
    print(f"📊 ASKS0 near-misses (<=1.005) [artifact branch]: {len(asks0_near)}")
    for total, q, yp, np in asks0_near[:5]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | {q}")
    # distribution of two-sided totals around the bracket zone
    buckets = {'lt_1.00': 0, '1.00_1.005': 0, '1.005_1.01': 0, '1.01_1.03': 0, 'ge_1.03': 0}
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        min_yes = float(min(yes_book.asks, key=lambda a: float(a['price']))['price'])
        min_no = float(min(no_book.asks, key=lambda a: float(a['price']))['price'])
        t = min_yes + min_no
        if t < 1.00:
            buckets['lt_1.00'] += 1
        elif t <= 1.005:
            buckets['1.00_1.005'] += 1
        elif t <= 1.01:
            buckets['1.005_1.01'] += 1
        elif t <= 1.03:
            buckets['1.01_1.03'] += 1
        else:
            buckets['ge_1.00'] += 1
    print(f"📈 Min-ask two-sided total buckets: {buckets}")
    print(f"   median-ish: lt1.00={buckets['lt_1.00']} (BRACKETS) | le1.005={buckets['lt_1.00']+buckets['1.00_1.005']} (near-miss threshold)")


asyncio.run(scan())
