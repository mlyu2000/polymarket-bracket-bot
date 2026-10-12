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

    opps = []
    near_misses = []
    priced = 0
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append((opp.total_cost, opp))
        else:
            if yes_book and no_book and yes_book.asks and no_book.asks:
                priced += 1
                # CORRECTED: best ask = min (asks are DESC-sorted from API)
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    opps.sort(key=lambda x: x[0])
    near_misses.sort()
    return dict(markets=len(markets), priced=priced, opps=opps, near=near_misses, t=scan_time)

r = asyncio.run(scan())
print(f"CORRECTED-BEST-ASK SCAN: {r['markets']} markets ({r['priced']} priced) in {r['t']:.1f}s")
print(f"BRACKETS (best-ask sum<1.00): {len(r['opps'])}")
for s, o in r['opps'][:10]:
    print(f"  {s:.3f} | Yes@{o.yes_price:.3f} No@{o.no_price:.3f} | edge={o.net_edge:.4f} | shares={o.max_shares} | liq={o.liquidity if hasattr(o,'liquidity') else '?'} | {o.market_question[:60] if hasattr(o,'market_question') else ''}")
print(f"NEAR-MISSES best-ask (<=1.005): {len(r['near'])}")
for total, q, yp, np_, liq in r['near'][:8]:
    print(f"  {total:.3f} | Yes@{yp:.3f} No@{np_:.3f} | liq={liq} | {q}")
