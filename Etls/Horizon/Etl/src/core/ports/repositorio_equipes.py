from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple


@dataclass
class GrupoCadastrado:
    """Grupo de pesquisa já gravado, com o que a sincronização do CNPq precisa."""

    id: int
    nome: str
    organizacao_id: int
    url_cnpq: Optional[str]


class RepositorioEquipes(ABC):
    """Persistência de equipes, grupos de pesquisa e membros.

    Implementações não fazem commit: quem chama controla a transação.
    """

    @abstractmethod
    def listar_grupos(self) -> List[GrupoCadastrado]:
        """Todos os grupos de pesquisa."""
        pass

    @abstractmethod
    def buscar_grupo_por_nome(self, nome: str) -> Optional[int]:
        """Id do grupo com esse nome (normalizado), ou None."""
        pass

    @abstractmethod
    def garantir_grupo(
        self,
        nome: str,
        organizacao_id: int,
        sigla: Optional[str] = None,
        descricao: Optional[str] = None,
    ) -> Tuple[int, bool]:
        """Id do grupo com esse nome e se ele foi criado agora.

        Um grupo que já existe é devolvido sem mudança.
        """
        pass

    @abstractmethod
    def definir_url_cnpq(self, grupo_id: int, url: str) -> bool:
        """Grava a URL do espelho CNPq. False se ela já é de outro grupo."""
        pass

    @abstractmethod
    def atualizar_equipe(
        self,
        equipe_id: int,
        nome: Optional[str] = None,
        descricao: Optional[str] = None,
    ) -> None:
        """Troca nome e/ou descrição da equipe (o que vier preenchido)."""
        pass

    @abstractmethod
    def definir_data_inicio_grupo(self, grupo_id: int, data_inicio: date) -> None:
        """Grava a data de formação do grupo."""
        pass

    @abstractmethod
    def adicionar_membro(
        self,
        equipe_id: int,
        pessoa_id: int,
        papel_id: int,
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> bool:
        """Grava o membro. False se a pessoa já tem esse papel na equipe."""
        pass

    @abstractmethod
    def definir_fim_membro(
        self, equipe_id: int, pessoa_id: int, papel_id: int, data_fim: date
    ) -> bool:
        """Grava a data de fim do membro (egresso). False se nada mudou."""
        pass
