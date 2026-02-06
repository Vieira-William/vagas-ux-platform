from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .database import engine, Base
from .api import vagas, stats, scraper

# Criar diretório data se não existir
os.makedirs("data", exist_ok=True)

# Criar tabelas no banco
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vagas UX Platform API",
    description="API para gerenciamento de vagas de UX/Product Design",
    version="1.0.0",
)

# CORS para permitir frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(vagas.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(scraper.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Vagas UX Platform API", "docs": "/docs"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
