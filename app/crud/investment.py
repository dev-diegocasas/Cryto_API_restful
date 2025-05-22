from bson import ObjectId
from pymongo.collection import Collection
from fastapi import HTTPException, status
from app.schemas.investment import (
    InvestmentCreate, InvestmentUpdate, InvestmentInDB
)
from app.services.coingecko import fetch_top_coins


async def create_investment(
    col: Collection,
    inv: InvestmentCreate
) -> InvestmentInDB:
    # Obtener precio actual
    coins = await fetch_top_coins(per_page=100)
    coin = next((c for c in coins if c["symbol"] == inv.symbol.lower()), None)
    if not coin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Cripto {inv.symbol} no encontrada")
    price = coin["current_price"]
    qty = inv.amount_usd / price

    # Insertar en MongoDB
    doc = inv.dict()
    doc.update({"price_usd": price, "qty": qty})
    res = col.insert_one(doc)

    # Construir respuesta explícita (evitar pasar _id en doc)
    return InvestmentInDB(
        id=str(res.inserted_id),
        symbol=inv.symbol,
        amount_usd=inv.amount_usd,
        price_usd=price,
        qty=qty
    )


def get_investment(
    col: Collection,
    investment_id: str
) -> InvestmentInDB:
    d = col.find_one({"_id": ObjectId(investment_id)})
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Inversión no encontrada")
    return InvestmentInDB(
        id=str(d["_id"]),
        symbol=d["symbol"],
        amount_usd=d["amount_usd"],
        price_usd=d["price_usd"],
        qty=d["qty"]
    )


async def update_investment(
    col: Collection,
    investment_id: str,
    inv_upd: InvestmentUpdate
) -> InvestmentInDB:
    # Fetch existing
    inv = get_investment(col, investment_id)
    # Calcular nuevo quantity
    new_amount = inv_upd.amount_usd if inv_upd.amount_usd is not None else inv.amount_usd
    # Reobtener precio actual
    coins = await fetch_top_coins(per_page=100)
    coin = next((c for c in coins if c["symbol"] == inv.symbol.lower()), None)
    price = coin["current_price"] if coin else inv.price_usd
    new_qty = new_amount / price

    update_fields = {"amount_usd": new_amount, "price_usd": price, "qty": new_qty}
    d = col.find_one_and_update(
        {"_id": ObjectId(investment_id)},
        {"$set": update_fields},
        return_document=True
    )
    if not d:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Inversión no encontrada")
    return InvestmentInDB(
        id=str(d["_id"]),
        **update_fields | {"symbol": d["symbol"]}
    )


def delete_investment(
    col: Collection,
    investment_id: str
) -> dict:
    res = col.delete_one({"_id": ObjectId(investment_id)})
    if res.deleted_count != 1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Inversión no encontrada")
    return {"ok": True}