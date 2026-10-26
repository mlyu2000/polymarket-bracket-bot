import asyncio, logging, json
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

TARGETS = [
    'Spread: FK Jablonec (-2.5)',
    'Spread: Lincoln Red Imps FC (-2.5)',
    'Spread: FC Thun (-2.5)',
    'Spread: FC Thun (-3.5)',
    'Spread: FK Jablonec (-3.5)',
    'Spread: FK Kauno Žalgiris (-1.5)',
    'Spread: Páfos FC (-2.5)',
    'Spread: Páfos FC (-3.5)',
    'Spread: FC Viktoria Plzeň (-3.5)',
]

FROZEN_Q = 'Bitcoin more valuable than any company before 2027?'

async def main():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    token_pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    all_books = await api.fetch_order_books_batch(token_pairs)

    print('=== dropped Spread markets: current state ===')
    for m, (yb, nb) in zip(markets, all_books):
        for t in TARGETS:
            if m.question[:60] == t or m.question[:58] == t[:58]:
                ya = len(yb.asks) if yb else 0
                na = len(nb.asks) if nb else 0
                if ya and na:
                    ymin = min(float(a['price']) for a in yb.asks)
                    nmin = min(float(a['price']) for a in nb.asks)
                    print(f"  {t}: two-sided sum={ymin+nmin:.4f} (Y@{ymin:.3f} N@{nmin:.3f}) liq={m.liquidity:.1f} asks Y{ya} N{na}")
                elif ya:
                    ymin = min(float(a['price']) for a in yb.asks)
                    print(f"  {t}: YES-only (min Y@{ymin:.3f}, {ya} asks) liq={m.liquidity:.1f} -> NOT bracketable")
                elif na:
                    nmin = min(float(a['price']) for a in nb.asks)
                    print(f"  {t}: NO-only (min N@{nmin:.3f}, {na} asks) liq={m.liquidity:.1f} -> NOT bracketable")
                else:
                    print(f"  {t}: no asks at all liq={m.liquidity:.1f}")

    print('=== frozen book check: Bitcoin>any-co ===')
    for m, (yb, nb) in zip(markets, all_books):
        if m.question.startswith('Bitcoin more valuable'):
            print(f"  liq raw: {m.liquidity}")
            ymin = min(float(a['price']) for a in yb.asks)
            nmin = min(float(a['price']) for a in nb.asks)
            print(f"  yes min-ask {ymin} asks_on_book={len(yb.asks)}; no min-ask {nmin} asks_on_book={len(nb.asks)}")
            print(f"  yes top3 sizes: {[a.get('size') for a in yb.asks[:3]]}")
            print(f"  no top3 sizes: {[a.get('size') for a in nb.asks[:3]]}")
            break

asyncio.run(main())
