# app/routers/investments_ui.py
from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo.collection import Collection
from bson import ObjectId

from app.db.mongo import get_collection
from app.schemas.investment import InvestmentCreate, InvestmentInDB, InvestmentUpdate
from app.crud.investment import create_investment, get_investment, update_investment, delete_investment

router = APIRouter(prefix="/investments", tags=["ui"])
templates = Jinja2Templates(directory="app/templates/investments")

def invest_col() -> Collection:
    return get_collection("investments")

@router.get("/", response_class=HTMLResponse)
async def view_list(request: Request, col: Collection = Depends(invest_col)):
    docs = [InvestmentInDB(
                id=str(d["_id"]),
                symbol=d["symbol"],
                amount_usd=d["amount_usd"],
                price_usd=d["price_usd"],
                qty=d["qty"]
            ) for d in col.find()]
    return templates.TemplateResponse("list.html", {"request": request, "investments": docs})

@router.get("/create", response_class=HTMLResponse)
async def view_create(request: Request):
    return templates.TemplateResponse("form.html", {"request": request, "action": "Crear", "investment": None})

@router.post("/create", response_class=HTMLResponse)
async def submit_create(
    request: Request,
    symbol: str = Form(...),
    amount_usd: float = Form(...),
    col: Collection = Depends(invest_col)
):
    inv = InvestmentCreate(symbol=symbol, amount_usd=amount_usd)
    await create_investment(col, inv)
    return RedirectResponse("/investments/", status_code=status.HTTP_302_FOUND)

@router.get("/{item_id}/edit", response_class=HTMLResponse)
async def view_edit(request: Request, item_id: str, col: Collection = Depends(invest_col)):
    d = col.find_one({"_id": ObjectId(item_id)})
    if not d:
        return RedirectResponse("/investments/")
    inv = InvestmentInDB(
        id=str(d["_id"]), symbol=d["symbol"],
        amount_usd=d["amount_usd"], price_usd=d["price_usd"], qty=d["qty"]
    )
    return templates.TemplateResponse("form.html", {"request": request, "action": "Editar", "investment": inv})

@router.post("/{item_id}/edit", response_class=HTMLResponse)
async def submit_edit(
    request: Request,
    item_id: str,
    symbol: str = Form(...),
    amount_usd: float = Form(...),
    col: Collection = Depends(invest_col)
):
    upd = InvestmentUpdate(amount_usd=amount_usd)
    await update_investment(col, item_id, upd)
    return RedirectResponse("/investments/", status_code=status.HTTP_302_FOUND)

@router.post("/{item_id}/delete", response_class=HTMLResponse)
async def submit_delete(request: Request, item_id: str, col: Collection = Depends(invest_col)):
    delete_investment(col, item_id)
    return RedirectResponse("/investments/", status_code=status.HTTP_302_FOUND)
