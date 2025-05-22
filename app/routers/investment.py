from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection
from app.db.mongo import get_collection
from app.schemas.investment import (
    InvestmentCreate, InvestmentInDB, InvestmentUpdate
)
from app.crud.investment import (
    create_investment, get_investment,
    update_investment, delete_investment
)

router = APIRouter(prefix="/items", tags=["items"])

# POST /items
@router.post("/", response_model=InvestmentInDB, status_code=status.HTTP_201_CREATED)
async def create_item(
    inv: InvestmentCreate,
    col: Collection = Depends(lambda: get_collection("investments"))
):
    return await create_investment(col, inv)

# GET /items/{id}
@router.get("/{item_id}", response_model=InvestmentInDB)
def read_item(
    item_id: str,
    col: Collection = Depends(lambda: get_collection("investments"))
):
    return get_investment(col, item_id)

# PUT /items/{id}
@router.put("/{item_id}", response_model=InvestmentInDB)
async def update_item(
    item_id: str,
    inv_upd: InvestmentUpdate,
    col: Collection = Depends(lambda: get_collection("investments"))
):
    return await update_investment(col, item_id, inv_upd)

# DELETE /items/{id}
@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_item(
    item_id: str,
    col: Collection = Depends(lambda: get_collection("investments"))
):
    return delete_investment(col, item_id)