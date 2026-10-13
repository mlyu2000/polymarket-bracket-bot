import asyncio, json, logging
import httpx

logging.basicConfig(level=logging.ERROR)

async def check():
    async with httpx.AsyncClient(timeout=30) as c:
        # fetch the event that WAS found
        r = await c.get("https://gamma-api.polymarket.com/events", params={"slug": "how-high-will-us-unemployment-go-in-2026"})
        evs = r.json()
        for e in evs:
            print(f"event: {e.get('slug')} active={e.get('active')} closed={e.get('closed')} title={e.get('title','')[:60]}")
            for m in e.get("markets", []):
                print(f"  mkt: {m.get('question','')[:80]}")
                print(f"       active={m.get('active')} closed={m.get('closed')} liq={m.get('liquidity')}")
                tokens = json.loads(m.get("clobTokenIds", "[]"))
                for i, tok in enumerate(tokens):
                    br = await c.get("https://clob.polymarket.com/book", params={"token_id": tok})
                    book = br.json()
                    asks = book.get("asks", [])
                    side = "YES" if i == 0 else "NO"
                    if asks:
                        mn = min(float(a["price"]) for a in asks)
                        print(f"       {side}: {len(asks)} asks min-ask={mn:.4f}")
                    else:
                        print(f"       {side}: no asks")
        # also search broader for the old slug
        for query in ["unemployment reach 6", "unemployment 6pt0", "us unemployment at least 6"]:
            r2 = await c.get("https://gamma-api.polymarket.com/public-search", params={"q": query})
            d2 = r2.json()
            slugs = [e.get("slug") for e in d2.get("events", [])][:8]
            print(f"search '{query}': {slugs}")

asyncio.run(check())
