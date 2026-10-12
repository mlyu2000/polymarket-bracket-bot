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

    both_asks = 0
    yes_only = 0
    no_only = 0
    neither = 0
    sums = []
    best_yes_sum = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        ya = yes_book and yes_book.asks
        na = no_book and no_book.asks
        if ya and na:
            both_asks += 1
            s = float(yes_book.asks[0]['price']) + float(no_book.asks[0]['price'])
            sums.append(s)
        elif ya and not na:
            yes_only += 1
        elif na and not ya:
            no_only += 1
        else:
            neither += 1

    sums.sort()
    buckets = {'<1.00': 0, '1.00-1.005': 0, '1.005-1.02': 0, '1.02-1.05': 0, '>=1.05': 0}
    for s in sums:
        if s < 1.00:
            buckets['<1.00'] += 1
        elif s < 1.005:
            buckets['1.00-1.005'] += 1
        elif s < 1.02:
            buckets['1.005-1.02'] += 1
        elif s < 1.05:
            buckets['1.02-1.05'] += 1
        else:
            buckets['>=1.05'] += 1

    return {
        'total': len(markets),
        'both_asks': both_asks,
        'yes_only': yes_only,
        'no_only': no_only,
        'neither': neither,
        'buckets': buckets,
        'min_sums': sums[:8],
        'median': sums[len(sums)//2] if sums else None,
    }

r = asyncio.run(scan())
print(f"total={r['total']} both_asks={r['both_asks']} yes_only={r['yes_only']} no_only={r['no_only']} neither={r['neither']}")
print(f"sum buckets (both-ask markets): {r['buckets']}")
print(f"8 lowest sums: {[f'{s:.4f}' for s in r['min_sums']]}")
print(f"median sum: {r['median']:.4f}" if r['median'] else "median: n/a")
