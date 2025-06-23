from .database import Base
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship

class Representante(Base):
    __tablename__ = 'representante'
    
    id_entidad = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(20), nullable=False)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    rfc = Column(String(20))
    contraseña = Column(String(50))

class Cliente(Base):
    __tablename__ = 'cliente'
    
    id_cliente = Column(Integer, primary_key=True, index=True)
    id_entidad = Column(Integer, ForeignKey('representante.id_entidad'))
    limite_credito = Column(Float)
    dias_credito = Column(Integer)
    
    representante = relationship("Representante")

class Agente(Base):
    __tablename__ = 'agente'
    
    id_agente = Column(Integer, primary_key=True, index=True)
    id_entidad = Column(Integer, ForeignKey('representante.id_entidad'))
    comision_venta = Column(Float)
    
    representante = relationship("Representante")

class Proveedor(Base):
    __tablename__ = 'proveedor'
    
    id_proveedor = Column(Integer, primary_key=True, index=True)
    id_entidad = Column(Integer, ForeignKey('representante.id_entidad'))
    tiempo_entrega = Column(Integer)
    
    representante = relationship("Representante")

class Contacto(Base):
    __tablename__ = 'contacto'
    
    id_contacto = Column(Integer, primary_key=True, index=True)
    id_entidad = Column(Integer, ForeignKey('representante.id_entidad'))
    nombre = Column(String(100), nullable=False)
    telefono = Column(String(20))
    email = Column(String(100))
    
    representante = relationship("Representante")

class Producto(Base):
    __tablename__ = 'producto'
    
    id_producto = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(30), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    id_familia = Column(Integer, ForeignKey('familia_producto.id_familia'))
    id_unidad_medida = Column(Integer, ForeignKey('unidad_medida.id_unidad'))
    peso = Column(Float)
    clave_sat = Column(String(8))
    
    familia = relationship("FamiliaProducto")
    unidad_medida = relationship("UnidadMedida")

# Nuevas tablas para ventas y facturas
class Factura(Base):
    __tablename__ = 'factura'
    
    id_factura = Column(Integer, primary_key=True, index=True)
    numero = Column(String(50), unique=True, nullable=False)
    fecha = Column(DateTime, nullable=False)
    id_cliente = Column(Integer, ForeignKey('cliente.id_cliente'))
    total = Column(Float, nullable=False)
    estado = Column(String(20), default='pendiente')
    
    cliente = relationship("Cliente")

class Venta(Base):
    __tablename__ = 'venta'
    
    id_venta = Column(Integer, primary_key=True, index=True)
    id_factura = Column(Integer, ForeignKey('factura.id_factura'))
    id_producto = Column(Integer, ForeignKey('producto.id_producto'))
    cantidad = Column(Float, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    
    factura = relationship("Factura")
    producto = relationship("Producto")