"""Endpoints de usuarios: /api/usuarios"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from musica_api.database import get_session
from musica_api.models import (
    Favorito,
    FavoritoRead,
    FavoritoReadConCancion,
    Usuario,
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
)
from musica_api.routers.favoritos import marcar_favorito

router = APIRouter()


def _obtener_o_404(session: Session, id: int) -> Usuario:
    usuario = session.get(Usuario, id)
    if not usuario:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return usuario


def _verificar_correo_libre(session: Session, correo: str, excluir_id: int | None = None):
    query = select(Usuario).where(Usuario.correo == correo)
    if excluir_id is not None:
        query = query.where(Usuario.id != excluir_id)
    if session.exec(query).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El correo ya está registrado")


@router.get("", response_model=list[UsuarioRead])
def listar_usuarios(
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    return session.exec(select(Usuario).offset(offset).limit(limit)).all()


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate, session: Session = Depends(get_session)):
    _verificar_correo_libre(session, datos.correo)
    usuario = Usuario.model_validate(datos)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.get("/{id}", response_model=UsuarioRead)
def obtener_usuario(id: int, session: Session = Depends(get_session)):
    return _obtener_o_404(session, id)


@router.put("/{id}", response_model=UsuarioRead)
def actualizar_usuario(
    id: int, datos: UsuarioUpdate, session: Session = Depends(get_session)
):
    usuario = _obtener_o_404(session, id)
    cambios = datos.model_dump(exclude_unset=True)
    if "correo" in cambios:
        _verificar_correo_libre(session, cambios["correo"], excluir_id=id)
    usuario.sqlmodel_update(cambios)
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(id: int, session: Session = Depends(get_session)):
    usuario = _obtener_o_404(session, id)
    session.delete(usuario)  # sus favoritos se eliminan en cascada
    session.commit()


# -----------------------------------------------------------------------------
# Favoritos de un usuario
# -----------------------------------------------------------------------------


@router.get("/{id}/favoritos", response_model=list[FavoritoReadConCancion])
def listar_favoritos_usuario(id: int, session: Session = Depends(get_session)):
    _obtener_o_404(session, id)
    return session.exec(select(Favorito).where(Favorito.id_usuario == id)).all()


@router.post(
    "/{id_usuario}/favoritos/{id_cancion}",
    response_model=FavoritoRead,
    status_code=status.HTTP_201_CREATED,
)
def marcar_favorito_usuario(
    id_usuario: int, id_cancion: int, session: Session = Depends(get_session)
):
    return marcar_favorito(session, id_usuario, id_cancion)


@router.delete(
    "/{id_usuario}/favoritos/{id_cancion}", status_code=status.HTTP_204_NO_CONTENT
)
def eliminar_favorito_usuario(
    id_usuario: int, id_cancion: int, session: Session = Depends(get_session)
):
    favorito = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == id_usuario, Favorito.id_cancion == id_cancion
        )
    ).first()
    if not favorito:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorito no encontrado")
    session.delete(favorito)
    session.commit()
