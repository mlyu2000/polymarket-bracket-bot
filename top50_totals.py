import asyncio, time
from config import Config
from polymarket_api import PolymarketAPI
from detector import BracketDetector

async def scan():
    Config.validate()
    api = PolymarketAPI()
    detector = BracketDetector()

    t0 = time.time()
    markets = await api.fetch_active_markets(limit=500)
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    results = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        if not yes_book or not no_book:
            continue
        if not yes_book.asks or not no_book.asks:
            continue
        # Use min ask logic as detector does
        yes_ask = min(yes_book.asks, key=lambda a: float(a["price"]))
        no_ask = min(no_book.asks, key=lambda a: float(a["price"]))
        yes_price = float(yes_ask["price"])
        no_price = float(no_ask["price"])
        total = yes_price + no_price
        # Determine which is yes/no by market outcome_prices? Actually token mapping may be arbitrary.
        # We assume token_pairs[0] is yes, token_pairs[1] is no per API. Let's trust.
        # Compute gross edge
        gross_edge = 1.0 - total
        results.append({
            'question': m.question[:80],
            'yes_price': yes_price,
            'no_price': no_price,
            'total': total,
            'gross_edge': gross_edge,
            'liquidity': m.liquidity,
            'active': m.active,
            'closed': m.closed,
        })
    # sort by total ascending
    results.sort(key=lambda x: x['total'])
    return results[:50]

res = asyncio.run(scan())
for r in res:
    print(f"{r['total']:.4f} edge {r['gross_edge']:.4f} | Yes@{r['yes_price']:.4f} No@{r['no_price']:.4f} | liq {r['liquidity']} | {r['question']}")
