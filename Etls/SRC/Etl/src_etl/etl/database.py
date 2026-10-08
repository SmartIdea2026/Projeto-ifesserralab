"""Configuração e modelos do banco de dados (SQLAlchemy) - Normalizado."""

from typing import List, Optional
from datetime import date
from sqlalchemy import String, Integer, Float, Boolean, Date, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

# Configuração de Conexão com Postgres (via Docker Local)
DATABASE_URL = "postgresql+psycopg2://etl_user:etl_password@localhost:5432/src_db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Campus(Base):
    __tablename__ = "campus"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, index=True)

class TipoAcao(Base):
    __tablename__ = "tipo_acao"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, index=True)

class TipoAtividade(Base):
    __tablename__ = "tipo_atividade"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, index=True)

class Fomento(Base):
    __tablename__ = "fomento"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, index=True)

class Natureza(Base):
    __tablename__ = "natureza"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, index=True)

class Funcao(Base):
    __tablename__ = "funcao"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(50), unique=True, index=True)


class Pessoa(Base):
    __tablename__ = "pessoa"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(255), index=True)
    cpf: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    vinculo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)


class Acao(Base):
    __tablename__ = "acao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    acao_original_id: Mapped[str] = mapped_column(String(50), unique=True, index=True) # Mantido por necessidade do ETL
    processo: Mapped[Optional[str]] = mapped_column(String(50), unique=False, index=True, nullable=True)
    titulo: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    data_cadastro: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    relatorio_aprovado: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    url_detalhe: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    fk_TipoAcao_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tipo_acao.id", ondelete="CASCADE"), nullable=True)
    fk_Coordenador_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pessoa.id", ondelete="SET NULL"), nullable=True)
    fk_Natureza_id: Mapped[Optional[int]] = mapped_column(ForeignKey("natureza.id", ondelete="CASCADE"), nullable=True)

    atividades: Mapped[List["Atividade"]] = relationship(back_populates="acao")


class Atividade(Base):
    __tablename__ = "atividade"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    atividade_original_id: Mapped[str] = mapped_column(String(50), unique=True, index=True) # Mantido por necessidade do ETL
    nome: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    fk_Acao_id: Mapped[int] = mapped_column(ForeignKey("acao.id", ondelete="CASCADE"))
    fk_TipoAtividade_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tipo_atividade.id", ondelete="CASCADE"), nullable=True)

    acao: Mapped["Acao"] = relationship(back_populates="atividades")


class AcaoVinculada(Base):
    __tablename__ = "acao_vinculada"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fk_AcaoVinculante_id: Mapped[Optional[int]] = mapped_column(ForeignKey("acao.id", ondelete="CASCADE"), nullable=True)
    fk_AcaoVinculada_id: Mapped[Optional[int]] = mapped_column(ForeignKey("acao.id", ondelete="CASCADE"), nullable=True)


class FinanciamentoAcao(Base):
    __tablename__ = "financiamento_acao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fk_Fomento_id: Mapped[Optional[int]] = mapped_column(ForeignKey("fomento.id", ondelete="RESTRICT"), nullable=True)
    fk_Acao_id: Mapped[Optional[int]] = mapped_column(ForeignKey("acao.id", ondelete="SET NULL"), nullable=True)


class LocalAcao(Base):
    __tablename__ = "local_acao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fk_Campus_id: Mapped[Optional[int]] = mapped_column(ForeignKey("campus.id", ondelete="RESTRICT"), nullable=True)
    fk_Acao_id: Mapped[Optional[int]] = mapped_column(ForeignKey("acao.id", ondelete="SET NULL"), nullable=True)


class EquipeExecucao(Base):
    __tablename__ = "equipe_execucao"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fk_Pessoa_id: Mapped[int] = mapped_column(ForeignKey("pessoa.id", ondelete="RESTRICT"), index=True)
    fk_Atividade_id: Mapped[int] = mapped_column(ForeignKey("atividade.id", ondelete="SET NULL"), index=True)
    fk_Funcao_id: Mapped[Optional[int]] = mapped_column(ForeignKey("funcao.id", ondelete="RESTRICT"), nullable=True)


class PublicoAlvo(Base):
    __tablename__ = "publico_alvo"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fk_Pessoa_id: Mapped[int] = mapped_column(ForeignKey("pessoa.id", ondelete="SET NULL"), index=True)
    fk_Atividade_id: Mapped[int] = mapped_column(ForeignKey("atividade.id", ondelete="SET NULL"), index=True)
    
    situacao: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    carga_horaria: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    certificado: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
