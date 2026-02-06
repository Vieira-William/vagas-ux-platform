from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class FonteEnum(str, Enum):
    indeed = "indeed"
    linkedin_jobs = "linkedin_jobs"
    linkedin_posts = "linkedin_posts"


class ModalidadeEnum(str, Enum):
    remoto = "remoto"
    hibrido = "hibrido"
    presencial = "presencial"
    nao_especificado = "nao_especificado"


class InglesEnum(str, Enum):
    nenhum = "nenhum"
    basico = "basico"
    intermediario = "intermediario"
    fluente = "fluente"
    nao_especificado = "nao_especificado"


class FormaContatoEnum(str, Enum):
    email = "email"
    link = "link"
    mensagem = "mensagem"
    indeed = "indeed"


class StatusEnum(str, Enum):
    pendente = "pendente"
    aplicada = "aplicada"
    descartada = "descartada"


class VagaBase(BaseModel):
    titulo: str = Field(..., max_length=200)
    empresa: Optional[str] = Field(None, max_length=100)
    tipo_vaga: Optional[str] = Field(None, max_length=50)
    fonte: FonteEnum
    link_vaga: Optional[str] = None
    localizacao: Optional[str] = Field(None, max_length=100)
    modalidade: Optional[ModalidadeEnum] = ModalidadeEnum.nao_especificado
    requisito_ingles: Optional[InglesEnum] = InglesEnum.nao_especificado
    forma_contato: Optional[FormaContatoEnum] = None
    email_contato: Optional[str] = Field(None, max_length=100)
    perfil_autor: Optional[str] = Field(None, max_length=200)
    nome_autor: Optional[str] = Field(None, max_length=100)
    data_coleta: date
    observacoes: Optional[str] = None


class VagaCreate(VagaBase):
    pass


class VagaUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=200)
    empresa: Optional[str] = Field(None, max_length=100)
    tipo_vaga: Optional[str] = Field(None, max_length=50)
    link_vaga: Optional[str] = None
    localizacao: Optional[str] = Field(None, max_length=100)
    modalidade: Optional[ModalidadeEnum] = None
    requisito_ingles: Optional[InglesEnum] = None
    forma_contato: Optional[FormaContatoEnum] = None
    email_contato: Optional[str] = Field(None, max_length=100)
    status: Optional[StatusEnum] = None
    observacoes: Optional[str] = None


class VagaResponse(VagaBase):
    id: int
    status: StatusEnum = StatusEnum.pendente
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VagaListResponse(BaseModel):
    total: int
    vagas: list[VagaResponse]


class StatsResponse(BaseModel):
    total_vagas: int
    por_fonte: dict[str, int]
    por_status: dict[str, int]
    por_modalidade: dict[str, int]
    por_tipo_vaga: dict[str, int]
    ultimas_24h: int
