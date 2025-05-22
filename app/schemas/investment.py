from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class InvestmentBase(BaseModel):
    symbol: str = Field(..., example="btc")
    amount_usd: float = Field(..., gt=0, example=100.0)

    model_config = ConfigDict(extra="forbid")

class InvestmentCreate(InvestmentBase):
    pass

class InvestmentUpdate(BaseModel):
    amount_usd: Optional[float] = Field(None, gt=0)

    model_config = ConfigDict(extra="forbid")

class InvestmentInDB(InvestmentBase):
    id: str
    price_usd: float
    qty: float

    model_config = ConfigDict(from_attributes=True)