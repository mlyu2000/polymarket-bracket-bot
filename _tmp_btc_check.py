import asyncio, json, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

async def main():
    Config.validate()
    api = PolymarketAPI()
    # find the BTC above-$72k Oct-16 market directly via gamma search
    url = ("https://gamma-api.polymarket.com/markets?limit=50&active=true&closed=false"
           "&order=volume24hr&ascending=false")
    found = []
    for page in range(4):
        u = url + f"&offset={page*50}"
        try:
            r = await api._request(u)
        except Exception as e:
            print("err", e); break
        ms = r if isinstance(r, list) else r.get('data', [])
        if not ms:
            break
        for m in ms:
            q = (m.get('question') or '')
            if 'Bitcoin' in q and '72,000' in q:
                found.append(m)
    print(f"matches: {len(found)}")
    for m in found:
        tids = m.get('clobTokenIds')
        if isinstance(tids, str):
            tids = json.loads(tids)
        print(f"Q: {m.get('question')}")
        print(f"  end={m.get('endDate')} closed={m.get('closed')} active={m.get('active')} "
              f"accepting={m.get('acceptingOrders')} liq={m.get('liquidity')}")
        print(f"  outcomes={m.get('outcomes')} tokens={tids}")
        if tids:
            books = await api.fetch_order_books_batch([(tids[0], tids[1])])
            yb, nb = books[0]
            def b(book, side):
                if not book: return None
                lst = getattr(book, side, None) or []
                return [float(a['price']) for a in lst]
            print(f"  YES asks={b(yb,'asks')} bids={b(yb,'bids')}")
            print(f"  NO  asks={b(nb,'asks')} bids={b(nb,'bids')}")
            ya, na = b(yb,'asks'), b(nb,'asks')
            if ya and na:
                print(f"  TRUE min-ask total = {min(ya)+min(na):.4f}  (asks[0] artifact = {ya[0]+na[0]:.4f})")

asyncio.run(main())
