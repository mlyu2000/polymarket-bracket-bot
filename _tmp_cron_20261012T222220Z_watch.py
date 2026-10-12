"""Targeted check: current min-ask sum for markets that dropped out of the band
(FC Porto -3.5, Wolves/Bolton O/U 3.5) plus the new entrants, vs 2141Z state."""
import asyncio, logging
from config import Config
from polymarket_api import PolymarketAPI

logging.basicConfig(level=logging.ERROR)

WATCH = [
    "Spread: FC Porto (-3.5)",
    "Wolverhampton Wanderers FC vs. Bolton Wanderers FC: O/U 3.5",
    "Spread: Manchester City FC (-3.5)",
    "Spread: Fenerbah",
    "Spread: \u0160K Slovan Bratislava (-3.5)",
    "Spread: \u0160K Slovan Bratislava (-2.5)",
    "Will the highest temperature in Atlanta be between 80-81",
    "Spread: Galatasaray SK (-2.5)",
    "Spread: Lincoln Red Imps FC (-2.5)",
    "Will Washington Capitals be the 2027 NHL Eastern Conference Champion?",
    "Spread: Real Madrid CF (-2.5)",
    "Spread: Burnley FC (-1.5)",
]

async def check():
    Config.validate()
    api = PolymarketAPI()
    markets = await api.fetch_active_markets()
    pairs = [(m.clob_token_ids[0], m.clob_token_ids[1]) for m in markets]
    books = await api.fetch_order_books_batch(pairs)
    print(f"{'total':>7} {'yes':>6} {'no':>6} {'liq':>10}  question")
    for m, (yb, nb) in zip(markets, books):
        if not any(w in m.question for w in WATCH):
            continue
        if yb and yb.asks and nb and nb.asks:
            yp = min(float(a['price']) for a in yb.asks)
            np_ = min(float(a['price']) for a in nb.asks)
            print(f"{yp+np_:7.4f} {yp:6.3f} {np_:6.3f} {m.liquidity:10.2f}  {m.question[:65]}")

asyncio.run(check())
