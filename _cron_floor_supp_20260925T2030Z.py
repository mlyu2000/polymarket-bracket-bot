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

    sums = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if yes_book and no_book and yes_book.asks and no_book.asks:
            yes_price = min(float(a['price']) for a in yes_book.asks)
            no_price = min(float(a['price']) for a in no_book.asks)
            sums.append((yes_price + no_price, m.question[:50], yes_price, no_price, m.liquidity))
    sums.sort()
    return {'markets': len(markets), 'priced': len(sums), 'sums': sums, 't': scan_time}

r = asyncio.run(scan())
print(f"🔍 Supplement (min-ask): {r['markets']} markets, {r['priced']} priced, {r['t']:.1f}s")
br = [s for s in r['sums'] if s[0] < 1.0]
nm = [s for s in r['sums'] if 1.0 <= s[0] <= 1.005]
print(f"✅ BRACKETS (min-ask sum < 1.00): {len(br)}")
for total, q, yp, np_, liq in br[:10]:
    print(f"  🔴 {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
print(f"📊 Near-misses (1.000–1.005): {len(nm)}")
for total, q, yp, np_, liq in nm[:10]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
if r['sums']:
    t, q, yp, np_, liq = r['sums'][0]
    print(f"📉 Best floor: {t:.3f} | Yes@{yp:.3f} No@{np_:.3f} | {q}")
