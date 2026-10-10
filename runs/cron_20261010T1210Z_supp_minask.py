import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    rows = []
    gross_lt1 = 0
    skipped = 0
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            skipped += 1
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or np <= 0 or yp >= 1.0 or np >= 1.0:
            skipped += 1
            continue
        total = yp + np
        if total < 1.0:
            gross_lt1 += 1
        rows.append((total, m.question[:55], yp, np, m.liquidity))
    rows.sort()
    print(f"markets={len(markets)} scored={len(rows)} skipped={skipped} gross_sum<1.00 count={gross_lt1}")
    print("--- best 12 (lowest sum) ---")
    for total, q, yp, np, liq in rows[:12]:
        print(f"{total:.4f} | Yes@{yp:.3f} No@{np:.3f} | liq={liq} | {q}")

asyncio.run(scan())
