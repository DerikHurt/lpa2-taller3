import platform
import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlmodel import Session

from musica_api.config import get_settings
from musica_api.database import create_db_and_tables, get_session
from musica_api.routers import canciones, favoritos, usuarios

settings = get_settings()
INICIO = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestor de ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Crear tablas en la base de datos
    create_db_and_tables()
    yield

    # Shutdown: Limpiar recursos si es necesario
    print("cerrando aplicación...")


app = FastAPI(
    title=settings.app_name,
    description="API RESTful para gestionar usuarios, canciones y favoritos",
    version=settings.app_version,
    lifespan=lifespan,
    contact={
        "name": "LPA2 - Taller 3",
        "url": "https://github.com/UR-CC/lpa2-taller3",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)


# Configurar CORS para permitir solicitudes desde diferentes orígenes
# (p. ej. el frontend del Taller 4 en http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(usuarios.router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(canciones.router, prefix="/api/canciones", tags=["Canciones"])
app.include_router(favoritos.router, prefix="/api/favoritos", tags=["Favoritos"])


@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raíz de la API.
    Retorna información básica y enlaces a la documentación.
    """
    return {
        "nombre": settings.app_name,
        "version": settings.app_version,
        "entorno": settings.environment,
        "documentacion": {"swagger": "/docs", "redoc": "/redoc"},
        "endpoints": {
            "usuarios": "/api/usuarios",
            "canciones": "/api/canciones",
            "favoritos": "/api/favoritos",
        },
    }


@app.get("/health", tags=["Health"])
def health_check(session: Session = Depends(get_session)):
    """
    Health check endpoint para verificar el estado de la API.
    Útil para sistemas de monitoreo y orquestación.
    """
    try:
        session.exec(text("SELECT 1"))
        estado_db = "ok"
    except Exception as e:  # noqa: BLE001
        estado_db = f"error: {e}"

    return {
        "status": "healthy" if estado_db == "ok" else "degraded",
        "database": estado_db,
        "uptime_segundos": round(time.time() - INICIO, 2),
        "python": platform.python_version(),
        "sistema": platform.system(),
    }


# TODO: Opcional - Agregar middleware para logging de requests


# TODO: Opcional - Agregar manejadores de errores personalizados


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
