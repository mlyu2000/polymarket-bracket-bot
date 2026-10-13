"""Supplementary min-ask scan — computes the TRUE bracket floor using min(all asks),
because Polymarket /book returns asks DESC-sorted (asks[0] = worst ask ~0.999).
Also verifies the tracked floor market (unemployment 6.0%) via direct CLOB /book.
Persists to runs/_tmp_cron_20261013T0338Z_supp_data.json.
"""
import asyncio, json, logging, time
import urllib.request
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)
TS = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
CLOB = 'https://clob.polymarket.com'


def fetch_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'bracket-scanner/1.0'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


async def supp():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(token_pairs)

    floors = []
    tiers = {'le1000': 0, 'le1005': 0, 'le1010': 0, 'le1020': 0, 'le1030': 0, 'le1050': 0}
    structural = {'two_sided': 0, 'yes_only': 0, 'no_only': 0, 'empty': 0}
    entries = []
    two_sided_totals = []
    for m, (yb, nb) in zip(markets, books):
        has_y = bool(yb and yb.asks)
        has_n = bool(nb and nb.asks)
        if has_y and has_n:
            structural['two_sided'] += 1
        elif has_y:
            structural['yes_only'] += 1
        elif has_n:
            structural['no_only'] += 1
        else:
            structural['empty'] += 1
        if has_y and has_n:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            total = round(yp + np_, 4)
            two_sided_totals.append(total)
            for key, thr in (('le1000', 1.0), ('le1005', 1.005), ('le1010', 1.01),
                             ('le1020', 1.02), ('le1030', 1.03), ('le1050', 1.05)):
                if total <= thr:
                    tiers[key] += 1
            if total <= 1.03:
                rec = {'total': total, 'q': m.question[:60],
                       'yes': round(yp, 4), 'no': round(np_, 4), 'liq': m.liquidity}
                entries.append(rec)
                floors.append((total, m.question[:50], round(yp, 4), round(np_, 4), m.liquidity))
    entries.sort(key=lambda e: e['total'])
    floors.sort()
    two_sided_totals.sort()
    median = two_sided_totals[len(two_sided_totals) // 2] if two_sided_totals else None

    # --- tracked floor market verification (direct CLOB /book) ---
    tracked = {}
    try:
        g = fetch_json('https://gamma-api.polymarket.com/public-search?q=unemployment%206.0%25')
        mkts = [x for ev in g.get('events', []) for x in ev.get('markets', [])
                if 'unemployment' in str(x.get('question', '')).lower()]
        for mk in mkts[:3]:
            q = mk.get('question')
            if 'unemployment' not in q.lower() or '6.0' not in q:
                continue
            toks = json.loads(mk['clobTokenIds']) if isinstance(mk.get('clobTokenIds'), str) else mk['clobTokenIds']
            b = fetch_json(CLOB + '/book?token_id=' + toks[0])
            asks = [float(x['price']) for x in b.get('asks', [])]
            bids = [float(x['price']) for x in b.get('bids', [])]
            tracked = {
                'q': q, 'active': mk.get('active'), 'closed': mk.get('closed'),
                'min_ask': min(asks) if asks else None,
                'max_bid': max(bids) if bids else None,
                'n_asks': len(asks), 'n_bids': len(bids),
                'liq': mk.get('liquidityNum'),
            }
            break
    except Exception as e:
        tracked = {'error': str(e)}

    out = {
        'ts': TS,
        'markets': len(markets),
        'scan': 'verbatim (asks[0]) + supplementary min-ask',
        'structural': structural,
        'not_bracketable_pct': round(100.0 * (structural['yes_only'] + structural['no_only'] + structural['empty']) / max(len(markets), 1), 1),
        'tiers': tiers,
        'median_two_sided_total': median,
        'floors_top10': floors[:10],
        'entries_top10': entries[:10],
        'tracked_floor_market': tracked,
    }
    with open(f'runs/_tmp_cron_{TS}_supp_data.json', 'w') as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))


asyncio.run(supp())
