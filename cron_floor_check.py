"""Min-ask floor check: Polymarket /book asks are DESC-sorted (asks[0]=worst).
True near-miss floor = min(all asks) per side. Persistent ops script (local, unpushed).
"""
import asyncio, logging, json, time
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

    floor_rows = []          # min-ask 2-sided floor
    yes_only = 0             # YES asks present, NO empty
    no_only = 0              # NO asks present, YES empty
    empty = 0                # both empty
    brackets = []

    for m, (yes_book, no_book) in zip(markets, all_books):
        y_asks = yes_book.asks if yes_book else []
        n_asks = no_book.asks if no_book else []
        if y_asks and n_asks:
            yp = min(float(a['price']) for a in y_asks)
            np_ = min(float(a['price']) for a in n_asks)
            total = yp + np_
            floor_rows.append((total, m.question[:60], yp, np_, m.liquidity))
            if total < 1.0:
                brackets.append((total, m.question[:60], yp, np_, m.liquidity))
        elif y_asks and not n_asks:
            yes_only += 1
        elif n_asks and not y_asks:
            no_only += 1
        else:
            empty += 1

    floor_rows.sort()
    two_sided = len(floor_rows)

    # liquidity of top floor candidates
    top = []
    for total, q, yp, np_, liq in floor_rows[:10]:
        top.append({'total': round(total, 4), 'yes': round(yp, 4), 'no': round(np_, 4),
                    'liq': liq, 'q': q})

    result = {
        'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'markets': len(markets),
        'scan_time': round(scan_time, 1),
        'brackets_min_ask': len(brackets),
        'two_sided': two_sided,
        'yes_only': yes_only,
        'no_only': no_only,
        'empty_both': empty,
        'not_bracketable_pct': round(100.0 * (len(markets) - two_sided) / len(markets), 1) if markets else 0,
        'floor_top10': top,
        'floor_history_bands': {
            'le_1_005': sum(1 for r in floor_rows if r[0] <= 1.005),
            'le_1_010': sum(1 for r in floor_rows if r[0] <= 1.010),
            'le_1_020': sum(1 for r in floor_rows if r[0] <= 1.020),
            'le_1_050': sum(1 for r in floor_rows if r[0] <= 1.050),
        },
    }
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return result

asyncio.run(scan())
