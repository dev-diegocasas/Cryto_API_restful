# app/routers/wallet.py
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.services.coingecko import fetch_top_coins

router = APIRouter(tags=["wallet"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/wallet/", response_class=HTMLResponse)
async def wallet_form(request: Request, vs: str = "usd", limit: int = 20):
    coins = await fetch_top_coins(vs_currency=vs, per_page=limit)
    return templates.TemplateResponse("wallet.html", {
        "request": request,
        "coins": coins,
        "vs": vs,
        "result": None
    })

@router.post("/wallet/", response_class=HTMLResponse)
async def wallet_submit(
    request: Request,
    symbol: str = Form(...),
    amount: float = Form(...),
    vs: str = Form("usd"),
    limit: int = Form(20)
):
    coins = await fetch_top_coins(vs_currency=vs, per_page=limit)
    # Busca la cripto seleccionada
    coin = next((c for c in coins if c["symbol"] == symbol.lower()), None)
    if not coin:
        raise HTTPException(404, f"Cripto '{symbol}' no encontrada")
    price = coin["current_price"]
    crypto_qty = amount / price
    result = {
        "symbol": symbol.upper(),
        "amount": amount,
        "price": price,
        "crypto_qty": round(crypto_qty, 8)
    }
    return templates.TemplateResponse("wallet.html", {
        "request": request,
        "coins": coins,
        "vs": vs,
        "result": result
    })
