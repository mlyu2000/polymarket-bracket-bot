import asyncio, logging, json, time
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
    brackets = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            brackets.append({'q': m.question[:60], 'sum': opp.total_cost, 'edge': opp.net_edge,
                             'yes': opp.yes_price, 'no': opp.no_price,
                             'shares': opp.max_shares, 'liq': m.liquidity})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ym = min(float(a['price']) for a in yes_book.asks)
            nm = min(float(a['price']) for a in no_book.asks)
            rows.append((ym + nm, m.question[:50], ym, nm, m.liquidity))

    rows.sort()
    return {'markets': len(markets), 'priced': len(rows), 'brackets': brackets, 'floor_rows': rows[:10]}

result = asyncio.run(scan())
print(f"markets={result['markets']} priced={result['priced']}")
print(f"MIN-ASK brackets (sum<1.00): {len(result['brackets'])}")
for b in result['brackets']:
    print(f"  {b['sum']:.4f} | Yes@{b['yes']:.3f} No@{b['no']:.3f} | {b['q']}")
nm = [r for r in result['floor_rows'] if r[0] > 1.0 and r[0] <= 1.005]
print(f"MIN-ASK near-misses (1.00<sum<=1.005): {len(nm)}")
for total, q, ym, n_, liq in nm:
    print(f"  {total:.4f} | Yes@{ym:.3f} No@{n_:.3f} | liq={liq} | {q}")
print("FLOOR top-5 (lowest raw best-ask sums):")
for total, q, ym, n_, liq in result['floor_rows'][:5]:
    print(f"  {total:.4f} | {q}")
