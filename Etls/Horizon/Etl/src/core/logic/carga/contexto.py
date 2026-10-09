"""Contexto da carga: conexão, repositórios, casamento de pessoas e relatório."""

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, Optional

import psycopg

from src.adapters.sinks.postgres.repositorio_areas_conhecimento import (
    RepositorioAreasConhecimentoPostgres,
)
from src.adapters.sinks.postgres.repositorio_equipes import RepositorioEquipesPostgres
from src.adapters.sinks.postgres.repositorio_formacoes import (
    RepositorioFormacoesPostgres,
)
from src.adapters.sinks.postgres.repositorio_iniciativas import (
    RepositorioIniciativasPostgres,
)
from src.adapters.sinks.postgres.repositorio_organizacoes import (
    RepositorioOrganizacoesPostgres,
)
from src.adapters.sinks.postgres.repositorio_pessoas import RepositorioPessoasPostgres
from src.adapters.sinks.postgres.repositorio_producoes import (
    RepositorioProducoesPostgres,
)
from src.core.logic.carga.pessoas import ControladorPessoasRepositorio
from src.core.logic.carga.relatorio import RelatorioCarga
from src.core.logic.person_matcher import PersonMatcher
from src.core.ports.repositorio_areas_conhecimento import RepositorioAreasConhecimento
from src.core.ports.repositorio_equipes import RepositorioEquipes
from src.core.ports.repositorio_formacoes import RepositorioFormacoes
from src.core.ports.repositorio_iniciativas import RepositorioIniciativas
from src.core.ports.repositorio_organizacoes import RepositorioOrganizacoes
from src.core.ports.repositorio_pessoas import RepositorioPessoas
from src.core.ports.repositorio_producoes import RepositorioProducoes


@dataclass
class ContextoCarga:
    """Tudo o que um carregador precisa para gravar no banco Horizon.

    Transações: ``passo`` envolve um passo inteiro (commit no fim) e
    ``registro`` envolve um registro (savepoint). Um erro dentro de ``registro``
    desfaz só aquele registro, entra no relatório e a carga segue.
    """

    conexao: psycopg.Connection
    pessoas: RepositorioPessoas
    organizacoes: RepositorioOrganizacoes
    formacoes: RepositorioFormacoes
    equipes: RepositorioEquipes
    areas: RepositorioAreasConhecimento
    iniciativas: RepositorioIniciativas
    producoes: RepositorioProducoes
    casamento_pessoas: PersonMatcher
    relatorio: RelatorioCarga

    @classmethod
    def criar(
        cls, conexao: psycopg.Connection, relatorio: Optional[RelatorioCarga] = None
    ) -> "ContextoCarga":
        pessoas = RepositorioPessoasPostgres(conexao)
        casamento = PersonMatcher(ControladorPessoasRepositorio(pessoas))
        casamento.preload_cache()
        return cls(
            conexao=conexao,
            pessoas=pessoas,
            organizacoes=RepositorioOrganizacoesPostgres(conexao),
            formacoes=RepositorioFormacoesPostgres(conexao),
            equipes=RepositorioEquipesPostgres(conexao),
            areas=RepositorioAreasConhecimentoPostgres(conexao),
            iniciativas=RepositorioIniciativasPostgres(conexao),
            producoes=RepositorioProducoesPostgres(conexao),
            casamento_pessoas=casamento,
            relatorio=relatorio or RelatorioCarga(),
        )

    @contextmanager
    def passo(self, nome: str) -> Iterator[None]:
        """Transação do passo. Um erro fora de ``registro`` desfaz o passo e sobe."""
        with self.conexao.transaction():
            yield
        self.relatorio.contar(nome, "concluido")

    @contextmanager
    def registro(self, passo: str, descricao: str) -> Iterator[None]:
        """Savepoint de um registro; o erro vira pendência e não interrompe a carga."""
        try:
            with self.conexao.transaction():
                yield
        except psycopg.OperationalError:
            # Conexão perdida: não adianta seguir registro por registro.
            raise
        except Exception as exc:
            self.relatorio.pular(passo, f"{type(exc).__name__}: {exc}", descricao)
            # O cache do casamento pode ter uma pessoa criada no registro desfeito.
            self.casamento_pessoas.preload_cache()
