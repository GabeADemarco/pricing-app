"""
Endpoints para gestión de facturas de compra
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime, UTC

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.usuario import Usuario
from app.models.factura_compra import (
    FacturaCompra, 
    FacturaCompraObservacion,
    RazonSocial,
    Logistica,
    Prioridad,
    FormaPago
)
from app.services.permisos_service import verificar_permiso

router = APIRouter(prefix="/facturas-compras", tags=["Facturas de Compra"])


# =============================================================================
# SCHEMAS
# =============================================================================

class FacturaCompraBase(BaseModel):
    """Schema base para facturas de compra"""
    razon_social: RazonSocial
    proveedor_id: Optional[int] = None
    proveedor_nombre: Optional[str] = None
    nro_proforma: Optional[str] = None
    link_proforma: Optional[str] = None
    logistica: Optional[Logistica] = None
    prioridad: Optional[Prioridad] = Prioridad.NORMAL
    nro_factura: Optional[str] = None
    link_factura: Optional[str] = None
    forma_pago: Optional[FormaPago] = None
    plazo: Optional[str] = None
    tipo_cambio: Optional[str] = None
    iniciado: Optional[bool] = False


class FacturaCompraCreate(FacturaCompraBase):
    """Schema para crear una nueva factura de compra"""
    pass


class FacturaCompraUpdate(BaseModel):
    """Schema para actualizar una factura de compra"""
    # Campos de COMPRAS
    razon_social: Optional[RazonSocial] = None
    proveedor_id: Optional[int] = None
    proveedor_nombre: Optional[str] = None
    nro_proforma: Optional[str] = None
    link_proforma: Optional[str] = None
    logistica: Optional[Logistica] = None
    prioridad: Optional[Prioridad] = None
    nro_factura: Optional[str] = None
    link_factura: Optional[str] = None
    forma_pago: Optional[FormaPago] = None
    plazo: Optional[str] = None
    tipo_cambio: Optional[str] = None
    iniciado: Optional[bool] = None
    listo_para_pagar: Optional[bool] = None
    
    # Campos de CARGA_OC_FC_GBP
    oc_cargada: Optional[bool] = None
    fc_cargada: Optional[bool] = None
    tiene_devoluciones: Optional[bool] = None
    rma_id: Optional[str] = None
    
    # Campos de DEPO
    retirado: Optional[bool] = None
    controlado: Optional[bool] = None
    
    # Campos de ADMIN
    pagado: Optional[bool] = None


class FacturaCompraResponse(BaseModel):
    """Schema de respuesta para facturas de compra"""
    id: int
    razon_social: RazonSocial
    fecha_carga: datetime
    proveedor_id: Optional[int] = None
    proveedor_nombre: Optional[str] = None
    nro_proforma: Optional[str] = None
    link_proforma: Optional[str] = None
    logistica: Optional[Logistica] = None
    prioridad: Optional[Prioridad] = None
    nro_factura: Optional[str] = None
    link_factura: Optional[str] = None
    forma_pago: Optional[FormaPago] = None
    plazo: Optional[str] = None
    tipo_cambio: Optional[str] = None
    iniciado: bool
    listo_para_pagar: bool
    
    # Campos de CARGA_OC_FC_GBP
    oc_cargada: bool
    oc_fecha: Optional[datetime] = None
    fc_cargada: bool
    fc_fecha: Optional[datetime] = None
    tiene_devoluciones: bool
    rma_id: Optional[str] = None
    
    # Campos de DEPO
    retirado: bool
    retirado_fecha: Optional[datetime] = None
    controlado: bool
    controlado_fecha: Optional[datetime] = None
    
    # Campos de TESORERIA
    pagado: bool
    pagado_fecha: Optional[datetime] = None
    
    # Auditoría
    created_at: datetime
    updated_at: Optional[datetime] = None
    creado_por_id: Optional[int] = None
    creado_por_nombre: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FacturaCompraListResponse(BaseModel):
    """Schema de respuesta para lista paginada"""
    total: int
    page: int
    page_size: int
    total_pages: int
    facturas: List[FacturaCompraResponse]


class ObservacionCreate(BaseModel):
    """Schema para crear una observación"""
    observacion: str = Field(..., min_length=1, max_length=5000)


class ObservacionResponse(BaseModel):
    """Schema de respuesta para observaciones"""
    id: int
    factura_compra_id: int
    rol_codigo: str
    usuario_id: Optional[int] = None
    observacion: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("", response_model=FacturaCompraListResponse)
async def listar_facturas_compras(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=1000, description="Cantidad de registros por página"),
    razon_social: Optional[RazonSocial] = Query(None, description="Filtrar por razón social"),
    listo_para_pagar: Optional[bool] = Query(None, description="Filtrar por listo para pagar"),
    oc_cargada: Optional[bool] = Query(None, description="Filtrar por OC cargada"),
    fc_cargada: Optional[bool] = Query(None, description="Filtrar por FC cargada"),
    retirado: Optional[bool] = Query(None, description="Filtrar por retirado"),
    controlado: Optional[bool] = Query(None, description="Filtrar por controlado"),
    pagado: Optional[bool] = Query(None, description="Filtrar por pagado"),
    search: Optional[str] = Query(None, description="Buscar por proveedor, nro factura o nro proforma"),
    creadas_por_mi: Optional[bool] = Query(None, description="Si es true, solo facturas creadas por el usuario actual"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista facturas de compra con filtros y paginación.
    Requiere permiso: facturas_compras.ver
    """
    if not verificar_permiso(db, current_user, 'facturas_compras.ver'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver facturas de compra"
        )
    
    query = db.query(FacturaCompra)
    
    # Aplicar filtros
    if razon_social:
        query = query.filter(FacturaCompra.razon_social == razon_social)
    
    if listo_para_pagar is not None:
        query = query.filter(FacturaCompra.listo_para_pagar == listo_para_pagar)
    
    if oc_cargada is not None:
        query = query.filter(FacturaCompra.oc_cargada == oc_cargada)
    
    if fc_cargada is not None:
        query = query.filter(FacturaCompra.fc_cargada == fc_cargada)
    
    if retirado is not None:
        query = query.filter(FacturaCompra.retirado == retirado)
    
    if controlado is not None:
        query = query.filter(FacturaCompra.controlado == controlado)
    
    if pagado is not None:
        query = query.filter(FacturaCompra.pagado == pagado)
    
    if creadas_por_mi:
        query = query.filter(FacturaCompra.creado_por_id == current_user.id)
    
    if search:
        search_filter = or_(
            FacturaCompra.proveedor_nombre.ilike(f"%{search}%"),
            FacturaCompra.nro_factura.ilike(f"%{search}%"),
            FacturaCompra.nro_proforma.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Filtrar por iniciado según rol:
    # - COMPRAS / ADMIN / SUPERADMIN: ven también borradores (iniciado = False)
    # - Otros roles: solo ven facturas con iniciado = True
    if current_user.rol_codigo not in ["COMPRAS", "ADMIN", "SUPERADMIN"]:
        query = query.filter(FacturaCompra.iniciado.is_(True))

    # Contar total
    total = query.count()
    
    # Aplicar paginación
    offset = (page - 1) * page_size
    facturas = query.order_by(FacturaCompra.fecha_carga.desc()).offset(offset).limit(page_size).all()
    
    total_pages = (total + page_size - 1) // page_size
    
    return FacturaCompraListResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        facturas=[FacturaCompraResponse.model_validate(f) for f in facturas]
    )


@router.get("/{factura_id}", response_model=FacturaCompraResponse)
async def obtener_factura_compra(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene una factura de compra por ID.
    Requiere permiso: facturas_compras.ver
    """
    if not verificar_permiso(db, current_user, 'facturas_compras.ver'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver facturas de compra"
        )
    
    factura = db.query(FacturaCompra).filter(FacturaCompra.id == factura_id).first()
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura de compra no encontrada"
        )
    
    return FacturaCompraResponse.model_validate(factura)


@router.delete("/{factura_id}", status_code=status.HTTP_204_NO_CONTENT)
async def eliminar_factura_borrador(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Elimina una factura de compra solo si está en borrador (iniciado = False).
    Pensado para que COMPRAS pueda descartar borradores antes de iniciar el proceso.
    """
    # Solo COMPRAS / ADMIN / SUPERADMIN (mismo permiso que editar campos de COMPRAS)
    if not verificar_permiso(db, current_user, 'facturas_compras.editar_campos_compras'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar facturas de compra"
        )

    factura = db.query(FacturaCompra).filter(FacturaCompra.id == factura_id).first()

    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura de compra no encontrada"
        )

    # Solo permitir eliminar borradores
    if factura.iniciado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden eliminar facturas en borrador (no iniciadas)"
        )

    db.delete(factura)
    db.commit()
    return


@router.post("", response_model=FacturaCompraResponse, status_code=status.HTTP_201_CREATED)
async def crear_factura_compra(
    factura: FacturaCompraCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea una nueva factura de compra.
    Requiere permiso: facturas_compras.crear
    """
    if not verificar_permiso(db, current_user, 'facturas_compras.crear'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear facturas de compra"
        )
    
    nueva_factura = FacturaCompra(
        **factura.model_dump(),
        creado_por_id=current_user.id
    )
    
    db.add(nueva_factura)
    db.commit()
    db.refresh(nueva_factura)
    
    return FacturaCompraResponse.model_validate(nueva_factura)


@router.patch("/{factura_id}", response_model=FacturaCompraResponse)
async def actualizar_factura_compra(
    factura_id: int,
    factura_update: FacturaCompraUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza una factura de compra.
    Requiere permisos específicos según el campo que se modifique.
    """
    factura = db.query(FacturaCompra).filter(FacturaCompra.id == factura_id).first()
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura de compra no encontrada"
        )
    
    # Verificar permisos según los campos que se actualizan
    update_data = factura_update.model_dump(exclude_unset=True)
    
    # Campos de COMPRAS (campos editables normales, excluyendo acciones especiales)
    campos_compras = {
        'razon_social', 'proveedor_id', 'proveedor_nombre', 'nro_proforma',
        'link_proforma', 'logistica', 'prioridad', 'nro_factura', 'link_factura',
        'forma_pago', 'plazo', 'tipo_cambio'
        # Nota: 'listo_para_pagar' NO está aquí porque tiene su propia verificación de permisos más abajo
    }
    if any(campo in update_data for campo in campos_compras):
        if not verificar_permiso(db, current_user, 'facturas_compras.editar_campos_compras'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para editar campos de COMPRAS"
            )
    
    # Marcar listo para pagar (acción especial con permiso específico)
    if 'listo_para_pagar' in update_data and update_data['listo_para_pagar']:
        if not verificar_permiso(db, current_user, 'facturas_compras.marcar_listo_pagar'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para marcar como listo para pagar"
            )
    
    # Campos de CARGA_OC_FC_GBP
    if 'oc_cargada' in update_data and update_data['oc_cargada']:
        if not verificar_permiso(db, current_user, 'facturas_compras.cargar_oc'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para cargar OC"
            )
        # Establecer fecha automáticamente
        update_data['oc_fecha'] = datetime.now(UTC)
    
    if 'fc_cargada' in update_data and update_data['fc_cargada']:
        if not verificar_permiso(db, current_user, 'facturas_compras.cargar_fc'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para cargar FC"
            )
        # Validar que esté retirado antes de cargar FC
        if not factura.retirado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cargar FC sin que la factura esté retirada"
            )
        # Establecer fecha automáticamente
        update_data['fc_fecha'] = datetime.now(UTC)
    
    # Campos de DEPO
    if 'retirado' in update_data and update_data['retirado']:
        if not verificar_permiso(db, current_user, 'facturas_compras.marcar_retirado'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para marcar como retirado"
            )
        # Establecer fecha automáticamente
        update_data['retirado_fecha'] = datetime.now(UTC)
    
    if 'controlado' in update_data and update_data['controlado']:
        if not verificar_permiso(db, current_user, 'facturas_compras.marcar_controlado'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para marcar como controlado"
            )
        # Validación soft: avisar si no hay OC pero no bloquear
        if not factura.oc_cargada:
            # Solo avisar, no bloquear
            pass
        # Establecer fecha automáticamente
        update_data['controlado_fecha'] = datetime.now(UTC)
    
    # Campos de TESORERIA
    if 'pagado' in update_data and update_data['pagado']:
        if not verificar_permiso(db, current_user, 'facturas_compras.marcar_pagado'):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para marcar como pagado"
            )
        # Establecer fecha automáticamente
        update_data['pagado_fecha'] = datetime.now(UTC)
    
    # Validar campos obligatorios al iniciar proceso
    if 'iniciado' in update_data and update_data['iniciado'] and not factura.iniciado:
        campos_faltantes = []
        
        # Campos obligatorios para iniciar proceso
        if not factura.razon_social:
            campos_faltantes.append('Razón Social')
        if not factura.proveedor_nombre or not factura.proveedor_nombre.strip():
            campos_faltantes.append('Proveedor')
        
        # Validar que haya al menos un documento completo (proforma o factura)
        tiene_proforma = (factura.nro_proforma and factura.nro_proforma.strip() and 
                         factura.link_proforma and factura.link_proforma.strip())
        tiene_factura = (factura.nro_factura and factura.nro_factura.strip() and 
                        factura.link_factura and factura.link_factura.strip())
        
        if not tiene_proforma and not tiene_factura:
            campos_faltantes.append('Al menos un documento completo (Proforma o Factura con número y link)')
        else:
            # Si tiene proforma parcial, validar que tenga ambos campos
            if (factura.nro_proforma and factura.nro_proforma.strip()) and not (factura.link_proforma and factura.link_proforma.strip()):
                campos_faltantes.append('Link Proforma (requerido si se especifica número)')
            if (factura.link_proforma and factura.link_proforma.strip()) and not (factura.nro_proforma and factura.nro_proforma.strip()):
                campos_faltantes.append('Nro Proforma (requerido si se especifica link)')
            
            # Si tiene factura parcial, validar que tenga ambos campos
            if (factura.nro_factura and factura.nro_factura.strip()) and not (factura.link_factura and factura.link_factura.strip()):
                campos_faltantes.append('Link Factura (requerido si se especifica número)')
            if (factura.link_factura and factura.link_factura.strip()) and not (factura.nro_factura and factura.nro_factura.strip()):
                campos_faltantes.append('Nro Factura (requerido si se especifica link)')
        
        if not factura.logistica:
            campos_faltantes.append('Logística')
        if not factura.prioridad:
            campos_faltantes.append('Prioridad')
        if not factura.forma_pago:
            campos_faltantes.append('Forma de Pago')
        
        if campos_faltantes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede iniciar el proceso. Faltan los siguientes campos obligatorios: {', '.join(campos_faltantes)}"
            )
    
    # Actualizar campos
    for field, value in update_data.items():
        setattr(factura, field, value)
    
    db.commit()
    db.refresh(factura)
    
    return FacturaCompraResponse.model_validate(factura)


@router.get("/{factura_id}/observaciones", response_model=List[ObservacionResponse])
async def listar_observaciones(
    factura_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista las observaciones de una factura de compra.
    Requiere permiso: facturas_compras.ver_observaciones
    """
    if not verificar_permiso(db, current_user, 'facturas_compras.ver_observaciones'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver observaciones"
        )
    
    factura = db.query(FacturaCompra).filter(FacturaCompra.id == factura_id).first()
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura de compra no encontrada"
        )
    
    observaciones = db.query(FacturaCompraObservacion).filter(
        FacturaCompraObservacion.factura_compra_id == factura_id
    ).order_by(FacturaCompraObservacion.created_at.desc()).all()
    
    return [ObservacionResponse.model_validate(obs) for obs in observaciones]


@router.post("/{factura_id}/observaciones", response_model=ObservacionResponse, status_code=status.HTTP_201_CREATED)
async def agregar_observacion(
    factura_id: int,
    observacion: ObservacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Agrega una observación a una factura de compra.
    Requiere permiso: facturas_compras.agregar_observacion
    """
    if not verificar_permiso(db, current_user, 'facturas_compras.agregar_observacion'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para agregar observaciones"
        )
    
    factura = db.query(FacturaCompra).filter(FacturaCompra.id == factura_id).first()
    
    if not factura:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Factura de compra no encontrada"
        )
    
    # Obtener el código del rol del usuario
    rol_codigo = current_user.rol_codigo
    
    nueva_observacion = FacturaCompraObservacion(
        factura_compra_id=factura_id,
        rol_codigo=rol_codigo,
        usuario_id=current_user.id,
        observacion=observacion.observacion
    )
    
    db.add(nueva_observacion)
    db.commit()
    db.refresh(nueva_observacion)
    
    return ObservacionResponse.model_validate(nueva_observacion)
