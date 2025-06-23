from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .. import database
from ..database import get_db

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def sql_terminal(request: Request):
    return request.app.templates.TemplateResponse(
        "sql_terminal.html", {"request": request}
    )

@router.post("/execute")
async def execute_sql(
    request: Request, 
    db: Session = Depends(get_db)
):
    form_data = await request.form()
    sql_query = form_data.get("sql_query")
    
    if not sql_query:
        raise HTTPException(status_code=400, detail="La consulta SQL no puede estar vacía")
    
    try:
        # Ejecutar la consulta SQL
        result = db.execute(sql_query)
        
        # Si es una consulta SELECT, obtener resultados
        if sql_query.strip().lower().startswith('select'):
            columns = [col[0] for col in result.cursor.description]
            rows = result.fetchall()
            return {
                "status": "success",
                "columns": columns,
                "rows": rows
            }
        else:
            db.commit()
            return {
                "status": "success",
                "message": f"Comando ejecutado. Filas afectadas: {result.rowcount}"
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))