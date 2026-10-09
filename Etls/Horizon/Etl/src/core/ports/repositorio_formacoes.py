from abc import ABC, abstractmethod
from typing import Optional, Tuple

# Valores aceitos pelo banco Horizon (CHECK de orientadores_formacao.papel).
PAPEIS_ORIENTACAO_FORMACAO = ("orientador", "coorientador")


class RepositorioFormacoes(ABC):
    """Persistência da formação acadêmica: tipos, formações e orientadores.

    Implementações não fazem commit: quem chama controla a transação.
    """

    @abstractmethod
    def garantir_tipo_formacao(self, nome: str) -> int:
        """Id do tipo de formação (grau) com esse nome, criando se preciso."""
        pass

    @abstractmethod
    def adicionar_formacao(
        self,
        pessoa_id: int,
        tipo_formacao_id: int,
        organizacao_id: int,
        curso: str,
        ano_inicio: int,
        ano_fim: Optional[int],
        titulo_tese: Optional[str],
    ) -> Tuple[int, bool]:
        """Grava a formação. Devolve o id e se ela foi criada agora
        (False quando já existe uma igual em todos os campos)."""
        pass

    @abstractmethod
    def adicionar_orientador(
        self, formacao_id: int, pessoa_id: int, papel: str
    ) -> bool:
        """Liga orientador ou coorientador à formação. False se já ligado."""
        pass
