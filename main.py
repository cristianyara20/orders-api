"""
Punto de entrada de la aplicación – Orders API con FastAPI + Uvicorn.
Equivalente al index.ts del proyecto original en Express/TypeScript.
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import order_router

# Cargar variables de entorno
load_dotenv()

PORT = int(os.getenv("PORT", "3000"))
ENV = os.getenv("ENV", "development")

# ─── Configuración de la App ─────────────────────────────────────

app = FastAPI(
    title="Orders API",
    version="1.0.0",
    description="API REST para la gestión de pedidos, clientes y productos.",
    docs_url="/api/v1/docs",       # Swagger UI  (igual que la versión TS)
    redoc_url="/api/v1/redoc",     # ReDoc (bonus de FastAPI)
    openapi_url="/api/v1/openapi.json",
)

# CORS (equivalente a app.use(cors()))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Rutas ────────────────────────────────────────────────────────

# Prefijo obligatorio según la guía
app.include_router(order_router, prefix="/api/v1")


@app.get("/", summary="Ruta raíz", tags=["Sistema"])
def read_root():
    return {
        "message": "Bienvenido a la Orders API",
        "documentation": "/api/v1/docs",
        "status": "active"
    }


# Health check
@app.get("/api/v1/health", summary="Estado del servicio", tags=["Sistema"])
def health_check():
    return {"status": "ok", "message": "API is running"}


# ─── Ejecución directa ───────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    print(f">>> Server is running on http://localhost:{PORT}")
    print(f">>> Docs available at http://localhost:{PORT}/api/v1/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=(ENV == "development"))
