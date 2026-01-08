cat <<EOF > main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Monta a pasta 'static' para servir CSS, JS e Imagens
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    # Busca o index.html dentro da pasta static
    return FileResponse(os.path.join("static", "index.html"))

@app.get("/api/status")
async def get_status():
    return {"status": "active", "service": "Money Layer"}
EOF