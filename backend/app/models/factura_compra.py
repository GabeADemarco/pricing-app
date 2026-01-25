"""
Modelo para el sistema de carga de facturas de compra.
Representa el proceso completo desde la carga inicial de la factura hasta el pago.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RazonSocial(str, enum.Enum):
    """Razón social de la empresa"""
    GRUPO_GAUSS = "Grupo Gauss"
    PASTORIZA = "Pastoriza"


class Logistica(str, enum.Enum):
    """Tipo de logística para la compra"""
    GAUSS = "GAUSS"
    PROVEEDOR = "PROVEEDOR"
    TERCERO = "TERCERO"


class Prioridad(str, enum.Enum):
    """Prioridad de la compra para depósito"""
    NORMAL = "NORMAL"
    URGENTE = "URGENTE"


class FormaPago(str, enum.Enum):
    """Forma de pago"""
    CONTADO = "CONTADO"
    CHEQUE = "CHEQUE"
    CTA_CTE = "CTA CTE"


class FacturaCompra(Base):
    """
    Modelo principal para el proceso de carga de facturas de compra.
    Contiene todos los campos necesarios para el flujo completo del proceso.
    """
    __tablename__ = "facturas_compras"

    # ID principal
    id = Column(Integer, primary_key=True, index=True)

    # =========================================================================
    # CAMPOS DE COMPRAS (carga inicial)
    # =========================================================================
    razon_social = Column(SQLEnum(RazonSocial), nullable=False, index=True)
    fecha_carga = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Proveedor (FK al ERP, por ahora nullable hasta integrar)
    proveedor_id = Column(Integer, nullable=True, index=True)  # FK a proveedores del ERP
    proveedor_nombre = Column(String(255), nullable=True)  # Nombre del proveedor (cache)
    
    nro_proforma = Column(String(100), nullable=True)
    link_proforma = Column(String(500), nullable=True)  # URL al cloud
    
    logistica = Column(SQLEnum(Logistica), nullable=True)
    prioridad = Column(SQLEnum(Prioridad), nullable=True, default=Prioridad.NORMAL)
    
    nro_factura = Column(String(100), nullable=True)
    link_factura = Column(String(500), nullable=True)  # URL al cloud
    
    forma_pago = Column(SQLEnum(FormaPago), nullable=True)
    plazo = Column(String(100), nullable=True)  # Texto libre
    tipo_cambio = Column(String(100), nullable=True)  # Ej: "1480 - 3%"
    
    listo_para_pagar = Column(Boolean, default=False, nullable=False, index=True)

    # =========================================================================
    # CAMPOS DE CARGA_OC_FC_GBP (carga de OC y FC en GBP/ERP)
    # =========================================================================
    oc_cargada = Column(Boolean, default=False, nullable=False, index=True)
    oc_fecha = Column(DateTime(timezone=True), nullable=True)
    
    fc_cargada = Column(Boolean, default=False, nullable=False, index=True)
    fc_fecha = Column(DateTime(timezone=True), nullable=True)
    
    # Devoluciones/RMA
    tiene_devoluciones = Column(Boolean, default=False, nullable=False)
    rma_id = Column(String(100), nullable=True)  # ID de RMA si aplica

    # =========================================================================
    # CAMPOS DE DEPO (Retiro y Control)
    # =========================================================================
    retirado = Column(Boolean, default=False, nullable=False, index=True)
    retirado_fecha = Column(DateTime(timezone=True), nullable=True)
    
    controlado = Column(Boolean, default=False, nullable=False, index=True)
    controlado_fecha = Column(DateTime(timezone=True), nullable=True)

    # =========================================================================
    # CAMPOS DE TESORERIA (Pago)
    # =========================================================================
    pagado = Column(Boolean, default=False, nullable=False, index=True)
    pagado_fecha = Column(DateTime(timezone=True), nullable=True)

    # =========================================================================
    # OBSERVACIONES (compartido por todos los roles)
    # =========================================================================
    # Las observaciones se guardan en tabla separada para permitir historial
    # Ver modelo CompraObservacion

    # =========================================================================
    # AUDITORÍA
    # =========================================================================
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Usuario que creó la compra
    creado_por_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True, index=True)
    
    # Relaciones
    creado_por = relationship("Usuario", foreign_keys=[creado_por_id])
    observaciones = relationship("FacturaCompraObservacion", back_populates="factura_compra", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FacturaCompra(id={self.id}, nro_factura='{self.nro_factura}', proveedor='{self.proveedor_nombre}')>"


class FacturaCompraObservacion(Base):
    """
    Observaciones de facturas de compra con historial por rol.
    Permite que cada rol agregue observaciones y se mantenga registro de quién escribió qué.
    """
    __tablename__ = "facturas_compras_observaciones"

    id = Column(Integer, primary_key=True, index=True)
    factura_compra_id = Column(Integer, ForeignKey('facturas_compras.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Rol que escribió la observación
    rol_codigo = Column(String(50), nullable=False, index=True)  # COMPRAS, CARGA_OC_FC_GBP, DEPO, TESORERIA
    
    # Usuario que escribió (opcional, para auditoría)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=True, index=True)
    
    # Contenido de la observación
    observacion = Column(Text, nullable=False)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relaciones
    factura_compra = relationship("FacturaCompra", foreign_keys=[factura_compra_id])
    usuario = relationship("Usuario", foreign_keys=[usuario_id])

    def __repr__(self):
        return f"<FacturaCompraObservacion(id={self.id}, factura_compra_id={self.factura_compra_id}, rol='{self.rol_codigo}')>"
