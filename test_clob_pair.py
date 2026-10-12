import httpx
token_yes = "19039930756738455783103072435880506034204446741177886400889371901235212597751"
token_no = "33740164601821693667331453865716790315281818279379504703738279486691357870183"
for token in [token_yes, token_no]:
    url = f"https://clob.polymarket.com/book?token_id={token}"
    resp = httpx.get(url, timeout=10)
    data = resp.json()
    print('token', token[:10])
    print('asks', data.get('asks')[:3])
    print('bids', data.get('bids')[:3])
