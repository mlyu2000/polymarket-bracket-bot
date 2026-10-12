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
    el = time.time() - t0

    # Best asks = min price across ask list (CLOB /book returns asks DESC-sorted,
    # so asks[0] is the WORST ask. Detector uses min(); replicate that here.)
    rows = []
    brackets = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        yp = min(float(a['price']) for a in yes_book.asks)
        np_ = min(float(a['price']) for a in no_book.asks)
        total = yp + np_
        priced += 1
        if total < 1.0:
            brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        elif total <= 1.005:
            rows.append((total, m.question[:60], yp, np_, m.liquidity))
    brackets.sort()
    rows.sort()
    print(f"⏱ best-ask fetch+compute: {el:.1f}s | markets: {len(markets)} priced: {priced}")
    print(f"🔴 TRUE BRACKETS (best-ask sum < 1.00): {len(brackets)}")
    for total, q, yp, np_, liq in brackets[:10]:
        print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    print(f"🟡 NEAR-MISS (1.00 <= best-ask sum <= 1.005): {len(rows)}")
    for total, q, yp, np_, liq in rows[:10]:
        print(f"  sum={total:.4f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
    # floor
    all_totals = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not (yes_book and no_book and yes_book.asks and no_book.asks):
            continue
        all_totals.append(min(float(a['price']) for a in yes_book.asks) + min(float(a['price']) for a in no_book.asks))
    if all_totals:
        print(f"📉 floor(best-ask sum)={min(all_totals):.4f} across {len(all_totals)} priced markets")

asyncio.run(scan())
