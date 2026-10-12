import asyncio, logging, time, json, os
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    n_books = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book or not yes_book.asks or not no_book.asks:
            continue
        n_books += 1
        y = min(float(a['price']) for a in yes_book.asks)
        n = min(float(a['price']) for a in no_book.asks)
        rows.append((y + n, y, n, m.question[:70], m.liquidity))
    rows.sort()
    return len(markets), n_books, rows

markets, n_books, rows = asyncio.run(scan())
print(f"=== min-ask corrected scan: {markets} markets, {n_books} priced ===")
brackets = [r for r in rows if r[0] < 1.0]
print(f"TRUE BRACKETS (min-ask sum < 1.000): {len(brackets)}")
for s, y, n, q, liq in brackets[:10]:
    print(f"  {s:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")
print("FLOOR (10 lowest min-ask sums):")
for s, y, n, q, liq in rows[:10]:
    print(f"  {s:.4f} | Yes@{y:.3f} No@{n:.3f} | liq={liq} | {q}")

out = {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
       'markets': markets, 'priced': n_books,
       'floor': rows[0][0] if rows else None,
       'true_brackets': len(brackets)}
os.makedirs('runs', exist_ok=True)
with open(os.path.join('runs', 'scan_20260922T1910Z_minask.json'), 'w') as f:
    json.dump(out, f, indent=2)
print("saved runs/scan_20260922T1910Z_minask.json")
