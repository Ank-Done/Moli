from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, database
from ..database import get_db

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def reportes_home(request: Request):
    return request.app.templates.TemplateResponse(
        "reportes/base.html", {"request": request}
    )

@router.get("/ventas", response_class=HTMLResponse)
async def reporte_ventas(request: Request, db: Session = Depends(get_db)):
    # Obtener datos de ventas
    ventas = db.query(models.Venta).all()
    
    # Calcular totales
    total_ventas = db.query(func.sum(models.Venta.subtotal)).scalar() or 0
    total_productos = db.query(func.sum(models.Venta.cantidad)).scalar() or 0
    
    # Productos más vendidos
    productos_mas_vendidos = db.query(
        models.Producto.nombre,
        func.sum(models.Venta.cantidad).label('total_cantidad')
    ).join(models.Venta).group_by(models.Producto.id_producto).order_by(func.sum(models.Venta.cantidad).desc()).limit(5).all()
    
    return request.app.templates.TemplateResponse(
        "reportes/ventas.html", 
        {
            "request": request,
            "ventas": ventas,
            "total_ventas": total_ventas,
            "total_productos": total_productos,
            "productos_mas_vendidos": productos_mas_vendidos
        }
    )

@router.get("/ventas-data")
async def ventas_data(db: Session = Depends(get_db)):
    # Datos para gráficos
    productos_mas_vendidos = db.query(
        models.Producto.nombre,
        func.sum(models.Venta.cantidad).label('total_cantidad')
    ).join(models.Venta).group_by(models.Producto.id_producto).order_by(func.sum(models.Venta.cantidad).desc()).limit(7).all()
    
    ventas_por_mes = db.query(
        func.extract('month', models.Factura.fecha).label('mes'),
        func.sum(models.Venta.subtotal).label('total_ventas')
    ).join(models.Factura).group_by('mes').order_by('mes').all()
    
    return {
        "productos_mas_vendidos": [
            {"producto": p[0], "cantidad": float(p[1])} for p in productos_mas_vendidos
        ],
        "ventas_por_mes": [
            {"mes": int(v[0]), "ventas": float(v[1])} for v in ventas_por_mes
        ]
    }