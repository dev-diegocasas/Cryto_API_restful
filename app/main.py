from fastapi import FastAPI
from app.routers.market import router as market_router
from app.routers.wallet import router as wallet_router
from app.routers.investment import router as items_router
from app.routers.investments_ui import router as ui_router

app = FastAPI(title="Crypto Market & Wallet & Investments")

app.include_router(market_router)
app.include_router(wallet_router)
app.include_router(items_router)   # API REST (/items)
app.include_router(ui_router)      # Vistas HTML (/investments)
