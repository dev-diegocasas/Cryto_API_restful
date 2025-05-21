from pydantic import BaseModel, Field, ConfigDict

class InvestmentCreate(BaseModel):
    symbol: str = Field(..., example="btc")
    amount_usd: float = Field(..., gt=0, example=100.0)

    # No permita campos extra
    model_config = ConfigDict(extra="forbid")

class InvestmentInDB(InvestmentCreate):
    id: str
    price_usd: float
    qty: float

    # Mapeo de atributos (Pydantic v2)
    model_config = ConfigDict(from_attributes=True)