from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import afastamentos, cargos, colaboradores, escalas, relatorios, zonas

settings = get_settings()

app = FastAPI(
    title="Gestão de Colaboradores — Cartórios Eleitorais TRE-CE",
    description="API para gestão de colaboradores, lotação, escalas e afastamentos dos cartórios eleitorais do TRE-CE.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zonas.router)
app.include_router(cargos.router)
app.include_router(colaboradores.router)
app.include_router(escalas.router)
app.include_router(afastamentos.router)
app.include_router(relatorios.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
