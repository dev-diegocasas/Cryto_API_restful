from fastapi import FastAPI
from app.routers import market, wallet, investment

app = FastAPI(title="Crypto Market & Wallet & Investments")

app.include_router(market.router)
app.include_router(wallet.router)
app.include_router(investment.router)
