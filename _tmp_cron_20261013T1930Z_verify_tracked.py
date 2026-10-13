import asyncio, json, logging
import httpx
from config import Config

logging.basicConfig(level=logging.ERROR)

async def verify():
    Config.validate()
    q = "will-us-unemployment-reach-at-least-6pt0-in-2026"
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get("https://gamma-api.polymarket.com/public-search", params={"q": "us-unemployment-reach-at-least-6"})
        data = r.json()
        evs = data.get("events", [])
        target = None
        for e in evs:
            if q in e.get("slug", ""):
                target = e
                break
        if not target:
            print("NOT FOUND in public-search events")
            for e in evs[:10]:
                print("  event:", e.get("slug"))
            return
        print(f"event: {target.get('slug')} | active={target.get('active')} closed={target.get('closed')}")
        for m in target.get("markets", []):
            print(f"  mkt: {m.get('question')[:80]}")
            print(f"       active={m.get('active')} closed={m.get('closed')} liq={m.get('liquidity')} vol={m.get('volume')}")
            tokens = json.loads(m.get("clobTokenIds", "[]"))
            books = []
            for i, tok in enumerate(tokens):
                br = await c.get(f"https://clob.polymarket.com/book", params={"token_id": tok})
                book = br.json()
                books.append(book)
                asks = book.get("asks", [])
                bids = book.get("bids", [])
                side = "YES" if i == 0 else "NO"
                if asks:
                    mn = min(float(a["price"]) for a in asks)
                    bb = float(bids[0]["price"]) if bids else None
                    print(f"       {side} {tok[:12]}...: {len(asks)} asks min-ask={mn:.4f} best-bid={bb}")
                else:
                    print(f"       {side}: no asks")
            ya = min(float(a["price"]) for a in books[0].get("asks", [])) if books[0].get("asks") else None
            na = min(float(a["price"]) for a in books[1].get("asks", [])) if books[1].get("asks") else None
            if ya is not None and na is not None:
                print(f"       >>> TRUE FLOOR: Y@{ya:.4f} + N@{na:.4f} = {ya+na:.4f}")

asyncio.run(verify())
