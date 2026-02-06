from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/stats", tags=["estatisticas"])


@router.get("/", response_model=schemas.StatsResponse)
def obter_estatisticas(db: Session = Depends(get_db)):
    """Retorna estatísticas gerais das vagas."""
    return crud.get_stats(db)
