import asyncio, logging, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

logging.basicConfig(level=logging.ERROR)

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks and m.liquidity > 0:
            # best ask = MINIMUM price (asks are DESC-sorted in CLOB payload)
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            total = yes_price + no_price
            priced += 1
            if total <= 1.005:
                near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    return {'markets': len(markets), 'priced': priced, 'near_misses': near_misses, 'scan_time': scan_time}

result = asyncio.run(scan())
print(f"🔍 Supp best-ask scan: {result['priced']}/{result['markets']} priced markets in {result['scan_time']:.1f}s")
print(f"📊 Near-misses (sum ≤ 1.005, best asks): {len(result['near_misses'])}")
for total, q, yp, np, liq in result['near_misses'][:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np:.3f} | liq=${liq:,.0f} | {q}")
