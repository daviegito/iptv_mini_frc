from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess

from database import engine
import models
import routes_auth
import routes_client

# Cria o arquivo do banco de dados (mini_iptv.db) e todas as tabelas caso não existam
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini-IPTV Backend")

# Habilitando CORS para o frontend (HTML/JS) se comunicar com a API sem bloqueios do navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas de Autenticação (/login e /me)
app.include_router(routes_auth.router)

# Registra as rotas de Streaming e Clientes (/channels e /play)
app.include_router(routes_client.router)

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Mini-IPTV!"}

@app.get("/system-check")
def system_check():
    """
    Endpoint simples de exemplo para testar se o ffmpeg está instalado no SO.
    Executa um comando no shell usando subprocess.
    """
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        primeira_linha = result.stdout.split('\n')[0] if result.stdout else "Sem saída"
        return {"status": "ok", "ffmpeg": primeira_linha}
    except FileNotFoundError:
        return {"status": "error", "ffmpeg": "ffmpeg não encontrado no PATH"}
