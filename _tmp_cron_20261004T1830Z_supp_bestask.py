import asyncio, logging, time, json
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    no_book_cnt = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            no_book_cnt += 1
            continue
        # best asks = MIN over ask levels (asks are DESC-sorted in CLOB API)
        yes_best = min(float(a['price']) for a in yes_book.asks)
        no_best = min(float(a['price']) for a in no_book.asks)
        total = yes_best + no_best
        rows.append((total, m.question[:55], yes_best, no_best, m.liquidity))

    rows.sort()
    brackets = [r for r in rows if r[0] < 1.0]
    near = [r for r in rows if 1.0 <= r[0] <= 1.005]
    print(f"markets={len(markets)} priced={len(rows)} unpriced={no_book_cnt}")
    print(f"BEST-ASK brackets (sum<1.00): {len(brackets)}")
    for total, q, yp, np, liq in brackets[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    print(f"BEST-ASK near-misses (1.000-1.005): {len(near)}")
    for total, q, yp, np, liq in near[:10]:
        print(f"  {total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")
    if rows:
        floor = rows[0][0]
        print(f"FLOOR (min best-ask sum): {floor:.4f}")

asyncio.run(supp())
