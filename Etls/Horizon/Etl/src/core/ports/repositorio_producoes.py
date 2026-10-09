from abc import ABC, abstractmethod
from typing import Optional, Tuple

# Tipos de produção que são artigos (periódico e congresso). Outras categorias
# do Lattes (produção técnica, patentes) entram sob demanda, com a chave do Lattes.
TIPO_ARTIGO = "artigo"
TIPO_TRABALHO_CONGRESSO = "trabalhos_completos_congressos"

# Valores genéricos decididos para produção sem ano e artigo sem veículo.
ANO_NAO_INFORMADO = 0
VEICULO_NAO_INFORMADO = "Não informado"


class RepositorioProducoes(ABC):
    """Persistência de produções, artigos, tipos e autores.

    Implementações não fazem commit: quem chama controla a transação.
    """

    @abstractmethod
    def garantir_tipo_producao(self, nome: str) -> int:
        """Id do tipo de produção com esse nome, criando se preciso."""
        pass

    @abstractmethod
    def garantir_artigo(
        self,
        titulo: str,
        ano: int,
        veiculo: str,
        tipo: str = TIPO_ARTIGO,
        volume: Optional[str] = None,
        paginas: Optional[str] = None,
        doi: Optional[str] = None,
    ) -> Tuple[int, bool]:
        """Id do artigo e se ele foi criado agora.

        Casa pelo DOI e, sem ele, por título exato + ano, como no ETL antigo.
        O link é montado a partir do DOI.
        """
        pass

    @abstractmethod
    def garantir_producao(self, titulo: str, ano: int, tipo: str) -> Tuple[int, bool]:
        """Id da produção (não artigo) e se foi criada agora; casa por título + ano + tipo."""
        pass

    @abstractmethod
    def adicionar_autor(self, producao_id: int, pessoa_id: int) -> bool:
        """Liga a pessoa como autora. False se já ligada."""
        pass
