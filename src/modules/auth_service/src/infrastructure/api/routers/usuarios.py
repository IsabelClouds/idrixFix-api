from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from src.shared.base import get_auth_db
from src.shared.common.responses import success_response, error_response
from src.modules.auth_service.src.infrastructure.db.repositories.usuario_repository import UsuarioRepository
from src.modules.auth_service.src.infrastructure.db.repositories.rol_repository import RolRepository
from src.modules.auth_service.src.application.use_cases.usuario_use_cases import UsuarioUseCase
from src.modules.auth_service.src.infrastructure.api.schemas.usuarios import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
)

router = APIRouter()

def get_usuario_use_case(db: Session = Depends(get_auth_db)) -> UsuarioUseCase:
    """Dependency para obtener el caso de uso de usuarios"""
    return UsuarioUseCase(
        usuario_repository=UsuarioRepository(db),
        rol_repository=RolRepository(db),
    )


@router.get("/", response_model=List[UsuarioResponse], status_code=status.HTTP_200_OK)
def get_usuarios(usuario_use_case: UsuarioUseCase = Depends(get_usuario_use_case)):
    """Obtiene lista de todos los usuarios con permisos por módulo"""
    data = usuario_use_case.get_all_usuarios()
    return success_response(
        data=[UsuarioResponse.model_validate(d).model_dump(mode="json") for d in data],
        message="Usuarios obtenidos"
    )


@router.get("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
def get_usuario(
    usuario_id: int, 
    usuario_use_case: UsuarioUseCase = Depends(get_usuario_use_case)
):
    """Obtiene un usuario por ID con permisos por módulo"""
    data = usuario_use_case.get_usuario_by_id(usuario_id)
    if not data:
        return error_response(
            message="Usuario no encontrado", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data=UsuarioResponse.model_validate(data).model_dump(mode="json"),
        message="Usuario obtenido"
    )


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def create_usuario(
    usuario_data: UsuarioCreate,
    usuario_use_case: UsuarioUseCase = Depends(get_usuario_use_case)
):
    """Crea un nuevo usuario con permisos por módulo"""
    new_data = usuario_use_case.create_usuario(usuario_data)
    return success_response(
        data=UsuarioResponse.model_validate(new_data).model_dump(mode="json"),
        message="Usuario creado",
        status_code=201
    )


@router.put("/{usuario_id}", response_model=UsuarioResponse, status_code=status.HTTP_200_OK)
def update_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    usuario_use_case: UsuarioUseCase = Depends(get_usuario_use_case)
):
    """Actualiza un usuario existente con permisos por módulo"""
    updated_data = usuario_use_case.update_usuario(usuario_id, usuario_data)
    if not updated_data:
        return error_response(
            message="Usuario no encontrado", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data=UsuarioResponse.model_validate(updated_data).model_dump(mode="json"),
        message="Usuario actualizado"
    )


@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def delete_usuario(
    usuario_id: int, 
    usuario_use_case: UsuarioUseCase = Depends(get_usuario_use_case)
):
    """Elimina (desactiva) un usuario"""
    deleted_data = usuario_use_case.delete_usuario(usuario_id)
    if not deleted_data:
        return error_response(
            message="Usuario no encontrado", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data={"id_usuario_eliminado": deleted_data.id_usuario},
        message="Usuario marcado como inactivo"
    )


@router.post("/{usuario_id}/activate", status_code=status.HTTP_200_OK)
def activate_usuario(
    usuario_id: int,
    usuario_use_case: UsuarioUseCase = Depends(get_usuario_use_case)
):
    """Activa un usuario"""
    activated_data = usuario_use_case.activate_usuario(usuario_id)
    if not activated_data:
        return error_response(
            message="Usuario no encontrado", 
            status_code=status.HTTP_404_NOT_FOUND
        )
    return success_response(
        data={"id_usuario_activado": activated_data.id_usuario},
        message="Usuario activado exitosamente"
    )
