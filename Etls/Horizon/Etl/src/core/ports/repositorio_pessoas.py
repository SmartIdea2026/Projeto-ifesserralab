from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional

# Valores aceitos pelo banco Horizon (CHECK de identificadores_pessoa.fonte) e
# níveis de proficiência decididos na migração para o PostgreSQL.
FONTES_IDENTIFICADOR = ("lattes", "sigpesq", "extensao", "egressos")
NIVEIS_PROFICIENCIA = ("alto", "medio", "basico", "nao_se_aplica")


@dataclass
class PessoaCadastrada:
    """Pessoa já gravada, com o que o casamento de pessoas precisa ler."""

    id: int
    nome: str
    emails: List[str] = field(default_factory=list)
    identificadores: Dict[str, str] = field(default_factory=dict)


class RepositorioPessoas(ABC):
    """Persistência da família pessoas: pessoas, e-mails, identificadores,
    perfil Lattes, prêmios, idiomas e proficiências.

    Implementações não fazem commit: quem chama controla a transação.
    """

    @abstractmethod
    def listar(self) -> List[PessoaCadastrada]:
        """Todas as pessoas, com e-mails (já em hash) e identificadores."""
        pass

    @abstractmethod
    def criar(self, nome: str, emails: Iterable[str] = ()) -> int:
        """Cria a pessoa, grava os e-mails e devolve o id."""
        pass

    @abstractmethod
    def adicionar_email(self, pessoa_id: int, email: str) -> bool:
        """Grava o e-mail em hash. False se ele já existe (nesta ou em outra pessoa)."""
        pass

    @abstractmethod
    def definir_identificador(self, pessoa_id: int, fonte: str, codigo: str) -> None:
        """Grava ou substitui o código da pessoa naquela fonte."""
        pass

    @abstractmethod
    def buscar_por_identificador(self, fonte: str, codigo: str) -> Optional[int]:
        """Id da pessoa com aquele código na fonte, ou None."""
        pass

    @abstractmethod
    def salvar_perfil_lattes(
        self,
        pessoa_id: int,
        resumo: str,
        nomes_citacao: str,
        atualizado_em: datetime,
    ) -> None:
        """Grava ou substitui o perfil Lattes da pessoa."""
        pass

    @abstractmethod
    def adicionar_premio(self, pessoa_id: int, titulo: str, ano: Optional[int]) -> bool:
        """Grava o prêmio. False se a pessoa já tem o mesmo título e ano."""
        pass

    @abstractmethod
    def garantir_idioma(self, nome: str) -> int:
        """Id do idioma com esse nome, criando se preciso."""
        pass

    @abstractmethod
    def definir_proficiencia(
        self,
        pessoa_id: int,
        idioma: str,
        leitura: str,
        escrita: str,
        fala: str,
        compreensao: str,
    ) -> bool:
        """Grava a proficiência. False se a pessoa já tem uma nesse idioma."""
        pass
