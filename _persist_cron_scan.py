"""Persist this cron run's scan data with corrected min-ask near-misses.
Follows established convention: runs/_tmp_cron_supp_data.json + verbose local commit.
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

    opps = []
    near_misses = []
    both_asks = 0
    yes_only = 0
    floor_entries = []

    for m, (yes_book, no_book) in zip(markets, all_books):
        opp = detector.detect(m, yes_book, no_book)
        if opp:
            opps.append({
                'q': m.question[:60],
                'yes': opp.yes_price,
                'no': opp.no_price,
                'sum': opp.total_cost,
                'edge': opp.net_edge,
                'shares': opp.max_shares,
                'liq': m.liquidity
            })
        else:
            yb = yes_book and yes_book.asks
            nb = no_book and no_book.asks
            if yb and nb:
                both_asks += 1
            elif (not yb) and nb:
                yes_only += 1
            # CORRECTED near-miss: min(all asks), NOT asks[0] (DESC-sorted artifact)
            if yb and nb:
                yes_price = min(float(a['price']) for a in yes_book.asks)
                no_price = min(float(a['price']) for a in no_book.asks)
                total = yes_price + no_price
                if 1.000 <= total <= 1.005:
                    near_misses.append((total, m.question[:50], yes_price, no_price, m.liquidity))

    near_misses.sort()
    floor_top = near_misses[:8]
    if near_misses:
        floor = near_misses[0][0]
        floor_leader = near_misses[0][1]
    else:
        floor = None
        floor_leader = None

    data = {
        'markets': len(markets),
        'opps': opps,
        'brackets': len(opps),
        'near_misses': near_misses,
        'near_misses_count': len(near_misses),
        'both_asks': both_asks,
        'yes_only': yes_only,
        'floor': floor,
        'floor_leader': floor_leader,
        'floor_top': floor_top,
        'scan_time': round(scan_time, 1),
    }
    with open('runs/_tmp_cron_supp_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    return data


if __name__ == '__main__':
    data = asyncio.run(scan())
    ts = time.strftime('%Y%m%dT%H%MZ', time.gmtime())
    msg = (f"Bracket scan {ts}: markets={data['markets']} "
           f"scan_time={data['scan_time']}s;"
           f"brackets={data['brackets']};"
           f"near_misses_le_1.005(min-ask)={data['near_misses_count']};"
           f"floor={data['floor']};"
           f"floor_leader={data['floor_leader']}@{data['floor_top'][0][2]:.3f}+{data['floor_top'][0][3]:.3f}")
    print(msg)
    print(f"both_asks={data['both_asks']} yes_only={data['yes_only']}")
    print(f"floor_top entries: {len(data['floor_top'])}")
    with open('_cron_commitmsg.txt', 'w') as f:
        f.write(msg + '\n')
