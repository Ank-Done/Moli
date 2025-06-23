from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .routers import catalogos, procesos, reportes, sql_terminal

app = FastAPI(
    title="Sistema de Gestión Moliendas y Alimentos",
    description="Plataforma integral para la gestión de azúcares y derivados",
    version="1.0.0"
)

# Configuración de archivos estáticos y templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Incluir routers
app.include_router(catalogos.router, prefix="/catalogos")
app.include_router(procesos.router, prefix="/procesos")
app.include_router(reportes.router, prefix="/reportes")
app.include_router(sql_terminal.router, prefix="/sql-terminal")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)