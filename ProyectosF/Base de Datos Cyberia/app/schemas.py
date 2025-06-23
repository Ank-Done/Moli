from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional

class RepresentanteBase(BaseModel):
    tipo: str
    codigo: str
    nombre: str
    rfc: Optional[str] = None

class RepresentanteCreate(RepresentanteBase):
    pass

class Representante(RepresentanteBase):
    id_entidad: int
    
    class Config:
        orm_mode = True

class ClienteBase(BaseModel):
    id_entidad: int
    limite_credito: Optional[float] = None
    dias_credito: Optional[int] = None

class ClienteCreate(ClienteBase):
    pass

class Cliente(ClienteBase):
    id_cliente: int
    representante: Representante
    
    class Config:
        orm_mode = True

class FacturaBase(BaseModel):
    numero: str
    fecha: datetime
    id_cliente: int
    total: float
    estado: Optional[str] = 'pendiente'

class FacturaCreate(FacturaBase):
    pass

class Factura(FacturaBase):
    id_factura: int
    
    class Config:
        orm_mode = True

class VentaBase(BaseModel):
    id_factura: int
    id_producto: int
    cantidad: float
    precio_unitario: float
    subtotal: float

class VentaCreate(VentaBase):
    pass

class Venta(VentaBase):
    id_venta: int
    producto: 'Producto'
    
    class Config:
        orm_mode = True

class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    id_familia: Optional[int] = None
    id_unidad_medida: Optional[int] = None
    peso: Optional[float] = None
    clave_sat: Optional[str] = None

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id_producto: int
    
    class Config:
        orm_mode = True