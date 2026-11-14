"""Endpoints de favoritos: /api/favoritos"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from musica_api.database import get_session
from musica_api.models import Cancion, Favorito, FavoritoCreate, FavoritoRead, Usuario

router = APIRouter()


def marcar_favorito(session: Session, id_usuario: int, id_cancion: int) -> Favorito:
    """Crea un favorito si existen usuario y canción y no está repetido."""
    if not session.get(Usuario, id_usuario):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if not session.get(Cancion, id_cancion):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Canción no encontrada")

    existente = session.exec(
        select(Favorito).where(
            Favorito.id_usuario == id_usuario, Favorito.id_cancion == id_cancion
        )
    ).first()
    if existente:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "La canción ya está en favoritos del usuario"
        )

    favorito = Favorito(id_usuario=id_usuario, id_cancion=id_cancion)
    session.add(favorito)
    session.commit()
    session.refresh(favorito)
    return favorito


@router.get("", response_model=list[FavoritoRead])
def listar_favoritos(
    session: Session = Depends(get_session),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
):
    return session.exec(select(Favorito).offset(offset).limit(limit)).all()


@router.post("", response_model=FavoritoRead, status_code=status.HTTP_201_CREATED)
def crear_favorito(datos: FavoritoCreate, session: Session = Depends(get_session)):
    return marcar_favorito(session, datos.id_usuario, datos.id_cancion)


@router.get("/{id}", response_model=FavoritoRead)
def obtener_favorito(id: int, session: Session = Depends(get_session)):
    favorito = session.get(Favorito, id)
    if not favorito:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorito no encontrado")
    return favorito


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_favorito(id: int, session: Session = Depends(get_session)):
    favorito = session.get(Favorito, id)
    if not favorito:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorito no encontrado")
    session.delete(favorito)
    session.commit()
