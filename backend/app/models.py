from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Index
from sqlalchemy.sql import func
from .database import Base


class Vaga(Base):
    __tablename__ = "vagas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(200), nullable=False)
    empresa = Column(String(100))
    tipo_vaga = Column(String(50))  # Product Designer, Product Manager, UX Designer, etc
    fonte = Column(String(20))  # 'indeed', 'linkedin_jobs', 'linkedin_posts'
    link_vaga = Column(Text)
    localizacao = Column(String(100))
    modalidade = Column(String(20))  # 'remoto', 'hibrido', 'presencial', 'nao_especificado'
    requisito_ingles = Column(String(50))  # 'nenhum', 'basico', 'intermediario', 'fluente', 'nao_especificado'
    forma_contato = Column(String(20))  # 'email', 'link', 'mensagem', 'indeed'
    email_contato = Column(String(100))
    perfil_autor = Column(String(200))  # Para LinkedIn posts
    nome_autor = Column(String(100))  # Para LinkedIn posts
    data_coleta = Column(Date, nullable=False)
    status = Column(String(20), default="pendente")  # 'pendente', 'aplicada', 'descartada'
    observacoes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index("idx_fonte", "fonte"),
        Index("idx_status", "status"),
        Index("idx_data_coleta", "data_coleta"),
        Index("idx_modalidade", "modalidade"),
    )

    def __repr__(self):
        return f"<Vaga(id={self.id}, titulo='{self.titulo}', empresa='{self.empresa}')>"
