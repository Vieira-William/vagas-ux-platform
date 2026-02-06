from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import crud, schemas
from ..scrapers.indeed import coletar_vagas_indeed
from ..scrapers.linkedin_jobs import coletar_vagas_linkedin
from ..scrapers.linkedin_posts import coletar_vagas_linkedin_posts

router = APIRouter(prefix="/scraper", tags=["scraper"])


def _salvar_vagas(db: Session, vagas_coletadas: list[dict], fonte: str):
    """Função auxiliar para salvar vagas no banco."""
    if not vagas_coletadas:
        return {"message": "Nenhuma vaga encontrada", "novas": 0, "total_coletadas": 0}

    vagas_novas = []
    for vaga_dict in vagas_coletadas:
        if not crud.check_duplicate(db, vaga_dict.get("titulo"), vaga_dict.get("empresa"), vaga_dict.get("link_vaga")):
            vaga = schemas.VagaCreate(**vaga_dict)
            vagas_novas.append(vaga)

    if not vagas_novas:
        return {
            "message": "Todas as vagas já existem no banco",
            "novas": 0,
            "total_coletadas": len(vagas_coletadas)
        }

    crud.create_vagas_batch(db, vagas_novas)

    return {
        "message": f"Coleta {fonte} concluída",
        "novas": len(vagas_novas),
        "total_coletadas": len(vagas_coletadas)
    }


@router.post("/indeed")
def executar_scraper_indeed(db: Session = Depends(get_db)):
    """Executa coleta de vagas do Indeed e salva no banco."""
    try:
        vagas_coletadas = coletar_vagas_indeed()
        return _salvar_vagas(db, vagas_coletadas, "Indeed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/linkedin")
def executar_scraper_linkedin(db: Session = Depends(get_db)):
    """Executa coleta de vagas do LinkedIn Jobs e salva no banco."""
    try:
        vagas_coletadas = coletar_vagas_linkedin()
        return _salvar_vagas(db, vagas_coletadas, "LinkedIn Jobs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/posts")
def executar_scraper_posts(db: Session = Depends(get_db)):
    """Executa coleta de vagas do LinkedIn Posts e salva no banco."""
    try:
        vagas_coletadas = coletar_vagas_linkedin_posts()
        return _salvar_vagas(db, vagas_coletadas, "LinkedIn Posts")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/all")
def executar_todos_scrapers(db: Session = Depends(get_db)):
    """Executa coleta de todas as fontes."""
    resultados = {}

    try:
        vagas_indeed = coletar_vagas_indeed()
        resultados["indeed"] = _salvar_vagas(db, vagas_indeed, "Indeed")
    except Exception as e:
        resultados["indeed"] = {"error": str(e)}

    try:
        vagas_linkedin = coletar_vagas_linkedin()
        resultados["linkedin_jobs"] = _salvar_vagas(db, vagas_linkedin, "LinkedIn Jobs")
    except Exception as e:
        resultados["linkedin_jobs"] = {"error": str(e)}

    try:
        vagas_posts = coletar_vagas_linkedin_posts()
        resultados["linkedin_posts"] = _salvar_vagas(db, vagas_posts, "LinkedIn Posts")
    except Exception as e:
        resultados["linkedin_posts"] = {"error": str(e)}

    total_novas = sum(r.get("novas", 0) for r in resultados.values() if isinstance(r, dict))

    return {
        "message": "Coleta completa",
        "total_novas": total_novas,
        "detalhes": resultados
    }
