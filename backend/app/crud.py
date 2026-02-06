from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from typing import Optional

from . import models, schemas


def get_vaga(db: Session, vaga_id: int) -> Optional[models.Vaga]:
    return db.query(models.Vaga).filter(models.Vaga.id == vaga_id).first()


def get_vagas(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    fonte: Optional[str] = None,
    status: Optional[str] = None,
    modalidade: Optional[str] = None,
    tipo_vaga: Optional[str] = None,
    requisito_ingles: Optional[str] = None,
) -> tuple[list[models.Vaga], int]:
    query = db.query(models.Vaga)

    if fonte:
        query = query.filter(models.Vaga.fonte == fonte)
    if status:
        query = query.filter(models.Vaga.status == status)
    if modalidade:
        query = query.filter(models.Vaga.modalidade == modalidade)
    if tipo_vaga:
        query = query.filter(models.Vaga.tipo_vaga == tipo_vaga)
    if requisito_ingles:
        query = query.filter(models.Vaga.requisito_ingles == requisito_ingles)

    total = query.count()
    vagas = query.order_by(models.Vaga.data_coleta.desc()).offset(skip).limit(limit).all()

    return vagas, total


def create_vaga(db: Session, vaga: schemas.VagaCreate) -> models.Vaga:
    db_vaga = models.Vaga(**vaga.model_dump())
    db.add(db_vaga)
    db.commit()
    db.refresh(db_vaga)
    return db_vaga


def create_vagas_batch(db: Session, vagas: list[schemas.VagaCreate]) -> list[models.Vaga]:
    db_vagas = [models.Vaga(**vaga.model_dump()) for vaga in vagas]
    db.add_all(db_vagas)
    db.commit()
    for vaga in db_vagas:
        db.refresh(vaga)
    return db_vagas


def update_vaga(db: Session, vaga_id: int, vaga_update: schemas.VagaUpdate) -> Optional[models.Vaga]:
    db_vaga = get_vaga(db, vaga_id)
    if not db_vaga:
        return None

    update_data = vaga_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vaga, field, value)

    db.commit()
    db.refresh(db_vaga)
    return db_vaga


def delete_vaga(db: Session, vaga_id: int) -> bool:
    db_vaga = get_vaga(db, vaga_id)
    if not db_vaga:
        return False

    db.delete(db_vaga)
    db.commit()
    return True


def get_stats(db: Session) -> dict:
    total = db.query(models.Vaga).count()

    # Por fonte
    por_fonte = dict(
        db.query(models.Vaga.fonte, func.count(models.Vaga.id))
        .group_by(models.Vaga.fonte)
        .all()
    )

    # Por status
    por_status = dict(
        db.query(models.Vaga.status, func.count(models.Vaga.id))
        .group_by(models.Vaga.status)
        .all()
    )

    # Por modalidade
    por_modalidade = dict(
        db.query(models.Vaga.modalidade, func.count(models.Vaga.id))
        .group_by(models.Vaga.modalidade)
        .all()
    )

    # Por tipo de vaga
    por_tipo_vaga = dict(
        db.query(models.Vaga.tipo_vaga, func.count(models.Vaga.id))
        .filter(models.Vaga.tipo_vaga.isnot(None))
        .group_by(models.Vaga.tipo_vaga)
        .all()
    )

    # Últimas 24h
    ontem = date.today() - timedelta(days=1)
    ultimas_24h = db.query(models.Vaga).filter(models.Vaga.data_coleta >= ontem).count()

    return {
        "total_vagas": total,
        "por_fonte": por_fonte,
        "por_status": por_status,
        "por_modalidade": por_modalidade,
        "por_tipo_vaga": por_tipo_vaga,
        "ultimas_24h": ultimas_24h,
    }


def check_duplicate(db: Session, titulo: str, empresa: Optional[str], link_vaga: Optional[str]) -> bool:
    """Verifica se já existe uma vaga com mesmo título + empresa ou mesmo link."""
    query = db.query(models.Vaga)

    if link_vaga:
        existing = query.filter(models.Vaga.link_vaga == link_vaga).first()
        if existing:
            return True

    if titulo and empresa:
        existing = query.filter(
            models.Vaga.titulo == titulo,
            models.Vaga.empresa == empresa
        ).first()
        if existing:
            return True

    return False
