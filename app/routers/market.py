# app/routers/market.py
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.coingecko import fetch_top_coins

router = APIRouter(tags=["market"])

templates = Jinja2Templates(directory="app/templates")

@router.get("/market/", response_class=HTMLResponse)
async def market_view(request: Request, vs: str = "usd", limit: int = 20):
    """
    Muestra la página 'Mercado Cripto de Hoy'.
    Query-params:
      - vs: moneda fiat (usd, eur…)
      - limit: cuántas criptos mostrar
    """
    coins = await fetch_top_coins(vs_currency=vs, per_page=limit)
    return templates.TemplateResponse("market.html", {
        "request": request,
        "coins": coins,
        "vs": vs
    })
