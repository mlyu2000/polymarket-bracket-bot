import asyncio, json, urllib.request
from polymarket_api import PolymarketAPI

async def main():
    api = PolymarketAPI()
    url = "https://gamma-api.polymarket.com/public-search?q=unemployment%20reach%20at%20least%206"
    req = urllib.request.Request(url, headers={'User-Agent': 'cron-verify'})
    data = json.loads(urllib.request.urlopen(req, timeout=30).read())
    target = None
    for e in data.get('events', []):
        for m in e.get('markets', []):
            q = m.get('question', '')
            if 'unemployment' in q.lower() and ('at least 6.0' in q or '6pt0' in m.get('slug', '')):
                target = (e.get('title'), q, m)
                break
        if target:
            break
    if not target:
        print("6.0% market not found in this event; dumping event markets:")
        for e in data.get('events', []):
            print(f"EVENT: {e.get('title','')}")
            for m in e.get('markets', []):
                print(f"  slug={m.get('slug','')[:60]} q={m.get('question','')[:60]}")
        return
    ev_title, q, m = target
    print(f"EVENT: {ev_title[:70]}")
    print(f"Q: {q[:80]}  slug={m.get('slug','')[:60]}")
    print(f"active={m.get('active')} closed={m.get('closed')}")
    toks = json.loads(m.get('clobTokenIds', '[]'))
    if not toks:
        print("no clobTokenIds")
        return
    yb = await api.fetch_order_book(toks[0])
    nb = await api.fetch_order_book(toks[1])
    yp = min(float(a['price']) for a in yb.asks) if yb and yb.asks else None
    np_ = min(float(a['price']) for a in nb.asks) if nb and nb.asks else None
    print(f"YES: {len(yb.asks) if yb and yb.asks else 0} asks, min-ask {yp:.4f}" if yp is not None else "YES: no asks")
    print(f"NO:  {len(nb.asks) if nb and nb.asks else 0} asks, min-ask {np_:.4f}" if np_ is not None else "NO: no asks")
    if yp is not None and np_ is not None:
        print(f"TRUE FLOOR: {yp + np_:.4f} (Y {yp:.4f} + N {np_:.4f})")

asyncio.run(main())
