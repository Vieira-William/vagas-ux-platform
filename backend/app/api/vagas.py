from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from .. import crud, schemas

router = APIRouter(prefix="/vagas", tags=["vagas"])


@router.get("/", response_model=schemas.VagaListResponse)
def listar_vagas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    fonte: Optional[str] = None,
    status: Optional[str] = None,
    modalidade: Optional[str] = None,
    tipo_vaga: Optional[str] = None,
    requisito_ingles: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Lista todas as vagas com filtros opcionais."""
    vagas, total = crud.get_vagas(
        db,
        skip=skip,
        limit=limit,
        fonte=fonte,
        status=status,
        modalidade=modalidade,
        tipo_vaga=tipo_vaga,
        requisito_ingles=requisito_ingles,
    )
    return {"total": total, "vagas": vagas}


@router.get("/{vaga_id}", response_model=schemas.VagaResponse)
def obter_vaga(vaga_id: int, db: Session = Depends(get_db)):
    """Obtém uma vaga específica por ID."""
    vaga = crud.get_vaga(db, vaga_id)
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga


@router.post("/", response_model=schemas.VagaResponse, status_code=201)
def criar_vaga(vaga: schemas.VagaCreate, db: Session = Depends(get_db)):
    """Cria uma nova vaga."""
    if crud.check_duplicate(db, vaga.titulo, vaga.empresa, vaga.link_vaga):
        raise HTTPException(status_code=400, detail="Vaga duplicada já existe")
    return crud.create_vaga(db, vaga)


@router.post("/batch", response_model=list[schemas.VagaResponse], status_code=201)
def criar_vagas_batch(vagas: list[schemas.VagaCreate], db: Session = Depends(get_db)):
    """Cria múltiplas vagas de uma vez (para importação)."""
    vagas_novas = []
    for vaga in vagas:
        if not crud.check_duplicate(db, vaga.titulo, vaga.empresa, vaga.link_vaga):
            vagas_novas.append(vaga)

    if not vagas_novas:
        raise HTTPException(status_code=400, detail="Todas as vagas já existem")

    return crud.create_vagas_batch(db, vagas_novas)


@router.patch("/{vaga_id}", response_model=schemas.VagaResponse)
def atualizar_vaga(vaga_id: int, vaga_update: schemas.VagaUpdate, db: Session = Depends(get_db)):
    """Atualiza uma vaga existente."""
    vaga = crud.update_vaga(db, vaga_id, vaga_update)
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga


@router.delete("/{vaga_id}", status_code=204)
def deletar_vaga(vaga_id: int, db: Session = Depends(get_db)):
    """Deleta uma vaga."""
    if not crud.delete_vaga(db, vaga_id):
        raise HTTPException(status_code=404, detail="Vaga não encontrada")


@router.patch("/{vaga_id}/status", response_model=schemas.VagaResponse)
def atualizar_status(
    vaga_id: int,
    status: schemas.StatusEnum,
    db: Session = Depends(get_db),
):
    """Atualiza apenas o status de uma vaga."""
    vaga = crud.update_vaga(db, vaga_id, schemas.VagaUpdate(status=status))
    if not vaga:
        raise HTTPException(status_code=404, detail="Vaga não encontrada")
    return vaga
