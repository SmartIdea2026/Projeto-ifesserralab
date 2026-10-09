from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

# Valores decididos na migração (situação) e aceitos pelo banco Horizon
# (CHECK de equipes_iniciativa.papel e organizacoes_iniciativa.papel).
SITUACOES_INICIATIVA = ("em_andamento", "concluida", "cancelada", "desconhecida")
PAPEIS_EQUIPE_INICIATIVA = ("executor", "parceiro")
PAPEIS_ORGANIZACAO_INICIATIVA = ("demandante", "financiadora", "parceira")
CAMPOS_ATUALIZAVEIS = (
    "nome",
    "situacao",
    "descricao",
    "data_inicio",
    "data_fim",
    "organizacao_id",
)


@dataclass
class IniciativaCadastrada:
    """Iniciativa já gravada, com o tipo pelo nome."""

    id: int
    nome: str
    tipo: str
    situacao: str
    organizacao_id: int
    descricao: Optional[str]
    data_inicio: Optional[date]
    data_fim: Optional[date]


class RepositorioIniciativas(ABC):
    """Persistência de iniciativas, hierarquia, participantes, bolsas e das
    ligações com equipes e organizações.

    Implementações não fazem commit: quem chama controla a transação.
    """

    @abstractmethod
    def tipo_iniciativa_id(self, nome: str) -> int:
        """Id de um tipo dos dados iniciais (projeto_pesquisa, orientacao...)."""
        pass

    @abstractmethod
    def criar(
        self,
        nome: str,
        tipo: str,
        organizacao_id: int,
        situacao: str,
        descricao: Optional[str] = None,
        data_inicio: Optional[date] = None,
        data_fim: Optional[date] = None,
    ) -> int:
        """Cria a iniciativa e devolve o id."""
        pass

    @abstractmethod
    def atualizar(self, iniciativa_id: int, campos: Dict[str, Any]) -> None:
        """Grava os campos informados (um de CAMPOS_ATUALIZAVEIS); None limpa o campo."""
        pass

    @abstractmethod
    def buscar(self, iniciativa_id: int) -> Optional[IniciativaCadastrada]:
        """A iniciativa com esse id, ou None."""
        pass

    @abstractmethod
    def buscar_por_nome(
        self, nome: str, tipo: Optional[str] = None
    ) -> List[IniciativaCadastrada]:
        """Iniciativas com exatamente esse nome (e tipo, se informado)."""
        pass

    @abstractmethod
    def listar(self, tipo: Optional[str] = None) -> List[IniciativaCadastrada]:
        """Todas as iniciativas (do tipo, se informado)."""
        pass

    @abstractmethod
    def definir_pai(self, iniciativa_id: int, pai_id: int) -> None:
        """Grava ou troca a iniciativa-mãe."""
        pass

    @abstractmethod
    def periodos_dos_filhos(
        self,
    ) -> Dict[int, Tuple[Optional[date], Optional[date]]]:
        """Para cada iniciativa-mãe, o menor início e o maior fim dos filhos."""
        pass

    @abstractmethod
    def adicionar_participante(
        self,
        iniciativa_id: int,
        pessoa_id: int,
        papel_id: int,
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> Tuple[int, bool]:
        """Id do participante e se foi criado agora. Repete-se só
        iniciativa + pessoa + papel."""
        pass

    @abstractmethod
    def garantir_bolsa(
        self, nome: str, financiador_id: int, valor: Union[Decimal, float]
    ) -> int:
        """Id da bolsa com esse nome e financiador; o valor só conta ao criar."""
        pass

    @abstractmethod
    def definir_bolsa_participante(self, participante_id: int, bolsa_id: int) -> None:
        """Liga ou troca a bolsa do participante."""
        pass

    @abstractmethod
    def ligar_equipe(self, iniciativa_id: int, equipe_id: int, papel: str) -> bool:
        """Liga a equipe (executor ou parceiro). False se já ligada."""
        pass

    @abstractmethod
    def ligar_organizacao(
        self, iniciativa_id: int, organizacao_id: int, papel: str
    ) -> bool:
        """Liga a organização (demandante, financiadora ou parceira). False se já ligada."""
        pass
