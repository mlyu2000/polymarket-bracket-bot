import asyncio, json, time
import httpx
from config import Config

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
QUERY = "will-us-unemployment-reach-at-least-6pt0-in-2026"


async def verify():
    Config.validate()
    ts = time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = {'ts': ts, 'query': QUERY}
    async with httpx.AsyncClient(timeout=20) as s:
        # 1) gamma public-search to locate event + markets + clobTokenIds
        r = await s.get(f"{GAMMA}/public-search", params={'q': QUERY})
        data = r.json()
        events = [e for e in data.get('events', []) if QUERY in (e.get('slug') or '')]
        if not events:
            # fall back: match by question substring
            events = [e for e in data.get('events', []) if 'unemployment' in json.dumps(e.get('title', '')).lower()]
        ev = events[0] if events else None
        out['event_found'] = bool(ev)
        if ev:
            out['event'] = {
                'title': ev.get('title'), 'slug': ev.get('slug'),
                'active': ev.get('active'), 'closed': ev.get('closed'),
                'endDate': ev.get('endDate') or ev.get('end_date'),
            }
        markets = ev.get('markets', []) if ev else []
        out['markets'] = len(markets)

        # 2) direct CLOB /book per token, true floor = min asks each side
        floors = []
        for m in markets:
            tids = m.get('clobTokenIds')
            if isinstance(tids, str):
                try:
                    tids = json.loads(tids)
                except Exception:
                    tids = None
            if not tids or len(tids) < 2:
                continue
            side = {}
            for i, label in ((0, 'yes'), (1, 'no')):
                r = await s.get(f"{CLOB}/book", params={'token_id': tids[i]})
                b = r.json()
                asks = b.get('asks', []) or []
                bids = b.get('bids', []) or []
                ask_p = min((float(a['price']) for a in asks), default=None)
                bid_p = max((float(b['price']) for b in bids), default=None)
                side[label] = {'min_ask': ask_p, 'n_asks': len(asks),
                               'max_bid': bid_p, 'n_bids': len(bids)}
            if side['yes']['min_ask'] is not None and side['no']['min_ask'] is not None:
                floor = round(side['yes']['min_ask'] + side['no']['min_ask'], 4)
            else:
                floor = None
            floors.append({
                'question': (m.get('question') or '')[:80],
                'yes': side['yes'], 'no': side['no'], 'true_floor': floor,
            })
        floors.sort(key=lambda x: (x['true_floor'] is None, x['true_floor']))
        out['floors'] = floors

    with open(f"runs/_tmp_cron_{ts}_verify_tracked.json", 'w') as f:
        json.dump(out, f, indent=2, default=str)
    print(f"VERIFY {ts}: {QUERY}")
    print(f"  event_found={out['event_found']} markets={out['markets']}")
    if ev:
        print(f"  event: {out['event']}")
    for fl in floors:
        print(f"  floor={fl['true_floor']} | Y min-ask={fl['yes']['min_ask']} ({fl['yes']['n_asks']} asks) max-bid={fl['yes']['max_bid']} ({fl['yes']['n_bids']} bids)"
              f" | N min-ask={fl['no']['min_ask']} ({fl['no']['n_asks']} asks) max-bid={fl['no']['max_bid']} ({fl['no']['n_bids']} bids)"
              f" | {fl['question']}")


asyncio.run(verify())
