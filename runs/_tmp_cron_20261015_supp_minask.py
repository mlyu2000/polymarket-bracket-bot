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
    two_sided = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yp = min(float(a['price']) for a in yes_book.asks)
            np_ = min(float(a['price']) for a in no_book.asks)
            total = yp + np_
            two_sided += 1
            rows.append((total, m.question[:70], yp, np_, m.liquidity))
    rows.sort()
    tiers = {
        'le1.050': sum(1 for r in rows if r[0] <= 1.050),
        'le1.020': sum(1 for r in rows if r[0] <= 1.020),
        'le1.010': sum(1 for r in rows if r[0] <= 1.010),
        'le1.005': sum(1 for r in rows if r[0] <= 1.005),
        'lt1.000': sum(1 for r in rows if r[0] < 1.000),
    }
    print(f"FLOOR-SCAN: {len(markets)} markets in {scan_time:.1f}s | two-sided {two_sided} | not-bracketable {len(markets)-two_sided}")
    print(f"TIERS: le1.050 n{tiers['le1.050']} | le1.020 n{tiers['le1.020']} | le1.010 n{tiers['le1.010']} | le1.005 n{tiers['le1.005']} | lt1.000 n{tiers['lt1.000']}")
    print("TOP-10 FLOOR (min-all-asks both legs):")
    for total, q, yp, np_, liq in rows[:10]:
        print(f"  {total:.4f} | Y{yp:.3f} N{np_:.3f} | liq {liq} | {q}")

asyncio.run(scan())
