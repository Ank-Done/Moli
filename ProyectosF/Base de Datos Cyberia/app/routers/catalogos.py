from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .. import models, schemas, database
from ..database import get_db

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def catalogos_home(request: Request):
    return request.app.templates.TemplateResponse(
        "catalogos/base.html", {"request": request}
    )

@router.get("/clientes", response_class=HTMLResponse)
async def listar_clientes(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).all()
    return request.app.templates.TemplateResponse(
        "catalogos/clientes.html", 
        {"request": request, "clientes": clientes}
    )

@router.get("/agentes", response_class=HTMLResponse)
async def listar_agentes(request: Request, db: Session = Depends(get_db)):
    agentes = db.query(models.Agente).all()
    return request.app.templates.TemplateResponse(
        "catalogos/agentes.html", 
        {"request": request, "agentes": agentes}
    )

@router.get("/contactos", response_class=HTMLResponse)
async def listar_contactos(request: Request, db: Session = Depends(get_db)):
    contactos = db.query(models.Contacto).all()
    return request.app.templates.TemplateResponse(
        "catalogos/contactos.html", 
        {"request": request, "contactos": contactos}
    )

@router.get("/proveedores", response_class=HTMLResponse)
async def listar_proveedores(request: Request, db: Session = Depends(get_db)):
    proveedores = db.query(models.Proveedor).all()
    return request.app.templates.TemplateResponse(
        "catalogos/proveedores.html", 
        {"request": request, "proveedores": proveedores}
    )

@router.get("/nuevo-representante", response_class=HTMLResponse)
async def nuevo_representante_form(request: Request):
    return request.app.templates.TemplateResponse(
        "catalogos/representante_form.html", {"request": request}
    )

@router.post("/crear-representante")
async def crear_representante(
    request: Request, 
    representante: schemas.RepresentanteCreate, 
    db: Session = Depends(get_db)
):
    # Validar datos
    if not representante.codigo or not representante.nombre:
        raise HTTPException(status_code=400, detail="Código y nombre son obligatorios")
    
    # Verificar si el código ya existe
    existing = db.query(models.Representante).filter(
        models.Representante.codigo == representante.codigo
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="El código ya está registrado")
    
    # Crear nuevo representante
    db_representante = models.Representante(**representante.dict())
    db.add(db_representante)
    db.commit()
    db.refresh(db_representante)
    
    # Crear entidad específica según el tipo
    if representante.tipo == 'cliente':
        db_cliente = models.Cliente(id_entidad=db_representante.id_entidad)
        db.add(db_cliente)
    elif representante.tipo == 'agente':
        db_agente = models.Agente(id_entidad=db_representante.id_entidad)
        db.add(db_agente)
    elif representante.tipo == 'proveedor':
        db_proveedor = models.Proveedor(id_entidad=db_representante.id_entidad)
        db.add(db_proveedor)
    
    db.commit()
    
    return {"message": "Representante creado exitosamente"}