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
            brackets.append({'q': m.question[:60], 'sum': opp.total_cost, 'edge': opp.net_edge})
        if yes_book and no_book and yes_book.asks and no_book.asks:
            ym = min(float(a['price']) for a in yes_book.asks)
            nm = min(float(a['price']) for a in no_book.asks)
            rows.append((ym + nm, m.question[:50], ym, nm, m.liquidity))

    rows.sort()
    priced = len(rows)
    return {'markets': len(markets), 'priced': priced, 'brackets': brackets, 'floor_rows': rows[:10]}

result = asyncio.run(scan())
print(f"markets={result['markets']} priced={result['priced']} detector_brackets={len(result['brackets'])}")
print("TOP min-ask sums (true floor):")
for total, q, ym, nm, liq in result['floor_rows']:
    print(f"  {total:.3f} | YesMin@{ym:.3f} NoMin@{nm:.3f} | liq={liq} | {q}")
with open('runs/scan_20260929T0758Z_floor.json', 'w') as f:
    json.dump(result, f, indent=2)
