import asyncio, json, time, datetime
from config import Config
from polymarket_api import PolymarketAPI

async def scan():
    Config.validate()
    api = PolymarketAPI()
    t0 = time.time()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)
    scan_time = time.time() - t0

    floors = []          # both-leg min-ask floors (TRUE bracket cost)
    both_asks = 0
    yes_only = 0
    no_asks_only = 0
    no_books = 0
    near_liq_top = []
    for m, (yes_book, no_book) in zip(markets, all_books):
        y_asks = [float(a['price']) for a in (yes_book.asks or [])] if yes_book else []
        n_asks = [float(a['price']) for a in (no_book.asks or [])] if no_book else []
        if y_asks and n_asks:
            both_asks += 1
            floor = min(y_asks) + min(n_asks)
            floors.append((floor, m.question[:70], min(y_asks), min(n_asks), m.liquidity))
        elif y_asks:
            yes_only += 1
        elif n_asks:
            no_asks_only += 1
        else:
            no_books += 1

    floors.sort()
    tiers = {'lt1.000': 0, 'le1.050': 0, 'le1.020': 0, 'le1.010': 0, 'le1.005': 0}
    for f, *_ in floors:
        if f < 1.000: tiers['lt1.000'] += 1
        if f <= 1.050: tiers['le1.050'] += 1
        if f <= 1.020: tiers['le1.020'] += 1
        if f <= 1.010: tiers['le1.010'] += 1
        if f <= 1.005: tiers['le1.005'] += 1

    # BTC above-$72k Oct-15 check (resolves 16:00Z today)
    btc = None
    for m, (yes_book, no_book) in zip(markets, all_books):
        if '72' in m.question and 'Bitcoin' in m.question:
            yb = sorted([float(a['price']) for a in (yes_book.asks or [])]) if yes_book else []
            ybids = sorted([float(b['price']) for b in (yes_book.bids or [])], reverse=True) if yes_book else []
            nb = sorted([float(a['price']) for a in (no_book.asks or [])]) if no_book else []
            nbids = sorted([float(b['price']) for b in (no_book.bids or [])], reverse=True) if no_book else []
            btc = {'q': m.question[:80], 'yes_asks': yb[:3], 'yes_bids': ybids[:3], 'no_asks': nb[:3], 'no_bids': nbids[:3], 'liq': m.liquidity}
            break

    data = {
        'ts': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
        'markets': len(markets),
        'scan_time': round(scan_time, 1),
        'both_asks': both_asks, 'yes_only': yes_only, 'no_asks_only': no_asks_only, 'no_books': no_books,
        'tiers': tiers,
        'top15': [(round(f, 4), q, round(y, 4), round(n, 4), l) for f, q, y, n, l in floors[:15]],
        'btc_72k': btc,
    }
    print(json.dumps(data, indent=1))
    with open('_cron_20261015T0030Z_supp_data.json', 'w') as f:
        json.dump(data, f, indent=1)

asyncio.run(scan())
