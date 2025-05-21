# app/routers/investment.py

from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo.collection import Collection

from app.db.mongo import get_collection
from app.schemas.investment import InvestmentCreate, InvestmentInDB
from app.services.coingecko import fetch_top_coins

# Importamos las funciones CRUD
from app.crud.investment import (
    create_investment,
    get_all_investments,
    get_investment,
    update_investment,
    delete_investment
)

router = APIRouter(prefix="/investments", tags=["investments"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/view", response_class=HTMLResponse)
async def view_investments(
    request: Request,
    col: Collection = Depends(lambda: get_collection("investments"))
):
    """
    Muestra la tabla con todas las inversiones guardadas en MongoDB.
    """
    inv_list = get_all_investments(col)
    return templates.TemplateResponse(
        "investments/list.html",
        {
            "request": request,
            "investments": inv_list
        }
    )


@router.get("/create", response_class=HTMLResponse)
async def create_form(request: Request):
    """
    Formulario vacío para crear nueva inversión.
    """
    return templates.TemplateResponse(
        "investments/form.html",
        {
            "request": request,
            "action": "Crear",
            "investment": None
        }
    )


@router.post("/create")
async def create_investment_form(
    request: Request,
    symbol: str = Form(...),
    amount_usd: float = Form(...),
    col: Collection = Depends(lambda: get_collection("investments"))
):
    """
    Procesa el formulario de creación:
    - Consulta CoinGecko para obtener precio actual.
    - Calcula qty = amount_usd / price.
    - Inserta en Mongo con create_investment(...)
    - Redirige a /investments/view
    """
    # 1) Fetch de CoinGecko (manejo básico de 429)
    try:
        coins = await fetch_top_coins(per_page=100)
    except HTTPException as e:
        if e.status_code == 503:
            raise HTTPException(503, "No se pudo obtener precio de la cripto. Intenta más tarde.")
        raise e

    # 2) Buscar la cripto por símbolo
    coin = next((c for c in coins if c["symbol"] == symbol.lower()), None)
    if not coin:
        raise HTTPException(404, f"Cripto «{symbol}» no encontrada en CoinGecko")

    # 3) Calcular price y qty
    price = coin["current_price"]
    qty = amount_usd / price

    # 4) Insertar en Mongo
    create_investment(col, InvestmentCreate(symbol=symbol, amount_usd=amount_usd), price_usd=price, qty=qty)

    # 5) Redirigir al listado
    return RedirectResponse(url="/investments/view", status_code=303)


@router.get("/{id}/edit", response_class=HTMLResponse)
async def edit_form(
    request: Request,
    id: str,
    col: Collection = Depends(lambda: get_collection("investments"))
):
    """
    Formulario precargado para editar la inversión.
    """
    inv = get_investment(col, id)
    if not inv:
        raise HTTPException(404, "Inversión no encontrada")
    return templates.TemplateResponse(
        "investments/form.html",
        {
            "request": request,
            "action": "Editar",
            "investment": inv
        }
    )


@router.post("/{id}/edit")
async def update_investment_form(
    request: Request,
    id: str,
    symbol: str = Form(...),
    amount_usd: float = Form(...),
    col: Collection = Depends(lambda: get_collection("investments"))
):
    """
    Procesa el formulario de edición:
    - Vuelve a consultar CoinGecko para precio actualizado
    - Recalcula qty
    - Llama a update_investment
    - Redirige a /investments/view
    """
    # 1) Nuevo fetch de CoinGecko
    try:
        coins = await fetch_top_coins(per_page=100)
    except HTTPException as e:
        if e.status_code == 503:
            raise HTTPException(503, "No se pudo obtener precio de la cripto. Intenta más tarde.")
        raise e

    # 2) Buscar la cripto por símbolo
    coin = next((c for c in coins if c["symbol"] == symbol.lower()), None)
    if not coin:
        raise HTTPException(404, f"Cripto «{symbol}» no encontrada en CoinGecko")

    # 3) Calcular price y qty
    price = coin["current_price"]
    qty = amount_usd / price

    # 4) Actualizar en Mongo
    update_investment(col, id, symbol, amount_usd, price, qty)

    # 5) Redirigir al listado
    return RedirectResponse(url="/investments/view", status_code=303)


@router.post("/{id}/delete")
async def delete_investment_form(
    id: str,
    col: Collection = Depends(lambda: get_collection("investments"))
):
    """
    Elimina la inversión con ObjectId == id y redirige a la lista.
    """
    delete_investment(col, id)
    return RedirectResponse(url="/investments/view", status_code=303)
