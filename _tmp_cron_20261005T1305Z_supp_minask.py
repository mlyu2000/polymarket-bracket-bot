import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def supp():
    api = PolymarketAPI()
    detector = BracketDetector()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    priced = 0
    empty_books = 0
    sums = []
    for m, (yb, nb) in zip(markets, all_books):
        if not yb or not nb or not yb.asks or not nb.asks:
            empty_books += 1
            continue
        yp = min(float(a['price']) for a in yb.asks)
        np_ = min(float(a['price']) for a in nb.asks)
        if yp <= 0 or yp >= 1 or np_ <= 0 or np_ >= 1:
            continue
        priced += 1
        sums.append((yp + np_, m.question[:60], yp, np_, m.liquidity))

    sums.sort()
    print(f"markets={len(markets)} priced={priced} empty_books={empty_books}")
    if sums:
        print(f"TRUE_FLOOR(min sum with min-ask): {sums[0][0]:.4f} | Yes@{sums[0][2]:.3f} No@{sums[0][3]:.3f} | liq={sums[0][4]} | {sums[0][1]}")
        print("TOP 8 lowest sums (min-ask method):")
        for s in sums[:8]:
            print(f"  {s[0]:.4f} | Yes@{s[2]:.3f} No@{s[3]:.3f} | liq={s[4]} | {s[1]}")
        n_lt1 = sum(1 for s in sums if s[0] < 1.0)
        n_le1005 = sum(1 for s in sums if s[0] <= 1.005)
        print(f"sums<1.000: {n_lt1} | sums<=1.005: {n_le1005}")

asyncio.run(supp())
