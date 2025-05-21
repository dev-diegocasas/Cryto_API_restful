# app/services/coingecko.py
import httpx
from typing import List, Dict

BASE = "https://api.coingecko.com/api/v3"

async def fetch_top_coins(vs_currency: str = "usd", per_page: int = 20) -> List[Dict]:
    """
    Trae las top `per_page` criptos por capitalización.
    """
    url = f"{BASE}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": 1,
        "sparkline": False
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()
