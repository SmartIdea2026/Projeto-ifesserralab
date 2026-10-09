from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional, Tuple

# Valores aceitos pelo banco Horizon (CHECK de organizacoes.tipo e papeis.escopo).
TIPOS_ORGANIZACAO = (
    "instituicao_ensino",
    "fomento",
    "empresa",
    "orgao_publico",
    "unidade",
)
ESCOPOS_PAPEL = ("vinculo", "equipe", "participacao")

# Papéis fixos de equipe e de participação, gravados nos dados iniciais.
# Papéis de vínculo vêm do Lattes (campo 'vinculo') e são criados sob demanda.
PAPEIS_FIXOS = {
    "participacao": (
        "coordenador",
        "pesquisador",
        "estudante",
        "orientador",
        "orientando",
    ),
    "equipe": ("lider", "pesquisador", "estudante", "tecnico"),
}


class RepositorioOrganizacoes(ABC):
    """Persistência de organizações, unidades (campi), papéis e vínculos.

    Implementações não fazem commit: quem chama controla a transação.
    """

    @abstractmethod
    def ifes_id(self) -> int:
        """Id do IFES, gravado nos dados iniciais."""
        pass

    @abstractmethod
    def garantir_organizacao(
        self, nome: str, tipo: str, sigla: Optional[str] = None
    ) -> int:
        """Id da organização com esse nome (ou sigla), criando com o tipo se preciso."""
        pass

    @abstractmethod
    def garantir_unidade(self, nome: str, organizacao_pai_id: int) -> int:
        """Id da unidade (campus) com esse nome sob a organização-mãe, criando se preciso."""
        pass

    @abstractmethod
    def listar_unidades(self, organizacao_pai_id: int) -> List[Tuple[int, str]]:
        """Unidades (id, nome) sob a organização-mãe, em ordem de criação."""
        pass

    @abstractmethod
    def garantir_papel(self, nome: str, escopo: str) -> int:
        """Id do papel. De equipe e participação, só os fixos; de vínculo, cria se preciso."""
        pass

    @abstractmethod
    def adicionar_vinculo(
        self,
        pessoa_id: int,
        organizacao_id: int,
        papel_id: int,
        data_inicio: Optional[date],
        data_fim: Optional[date],
    ) -> bool:
        """Grava o vínculo. False se já existe com a mesma organização, papel e início."""
        pass
