# app/crud/investment.py

from bson import ObjectId
from pymongo.collection import Collection
from app.schemas.investment import InvestmentCreate, InvestmentInDB
from pymongo.errors import PyMongoError
from fastapi import HTTPException

def create_investment(
    col: Collection,
    inv: InvestmentCreate,
    price_usd: float,
    qty: float
) -> InvestmentInDB:
    """
    Inserta una nueva inversión y devuelve InvestmentInDB.
    """
    doc = inv.dict()
    doc.update({
        "price_usd": price_usd,
        "qty": qty
    })
    try:
        res = col.insert_one(doc)
    except PyMongoError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al guardar en MongoDB: {e}"
        )
    return InvestmentInDB(
        id=str(res.inserted_id),
        **inv.dict(),
        price_usd=price_usd,
        qty=qty
    )

def get_all_investments(col: Collection) -> list[InvestmentInDB]:
    """
    Devuelve una lista de todas las inversiones en la colección.
    """
    out: list[InvestmentInDB] = []
    for d in col.find():
        out.append(InvestmentInDB(
            id=str(d["_id"]),
            symbol=d["symbol"],
            amount_usd=d["amount_usd"],
            price_usd=d["price_usd"],
            qty=d["qty"]
        ))
    return out

def get_investment(col: Collection, id: str) -> InvestmentInDB | None:
    """
    Busca una inversión por su ID. Si no existe o el ID es inválido, devuelve None.
    """
    try:
        oid = ObjectId(id)
    except Exception:
        return None

    d = col.find_one({"_id": oid})
    if not d:
        return None
    return InvestmentInDB(
        id=str(d["_id"]),
        symbol=d["symbol"],
        amount_usd=d["amount_usd"],
        price_usd=d["price_usd"],
        qty=d["qty"]
    )

def update_investment(
    col: Collection,
    id: str,
    symbol: str,
    amount_usd: float,
    price_usd: float,
    qty: float
) -> InvestmentInDB:
    """
    Actualiza una inversión existente. Lanza HTTPException(404) si no la encuentra.
    """
    try:
        oid = ObjectId(id)
    except Exception:
        raise HTTPException(status_code=404, detail="ID inválido")

    result = col.update_one(
        {"_id": oid},
        {"$set": {
            "symbol": symbol,
            "amount_usd": amount_usd,
            "price_usd": price_usd,
            "qty": qty
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")

    return InvestmentInDB(
        id=id,
        symbol=symbol,
        amount_usd=amount_usd,
        price_usd=price_usd,
        qty=qty
    )

def delete_investment(col: Collection, id: str):
    """
    Borra una inversión. No lanza error si no existe.
    """
    try:
        oid = ObjectId(id)
    except Exception:
        return
    col.delete_one({"_id": oid})
