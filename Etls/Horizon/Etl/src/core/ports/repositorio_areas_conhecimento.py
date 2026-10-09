from abc import ABC, abstractmethod


class RepositorioAreasConhecimento(ABC):
    """Persistência das áreas de conhecimento e de suas ligações.

    Implementações não fazem commit: quem chama controla a transação.
    """

    @abstractmethod
    def garantir_area(self, nome: str) -> int:
        """Id da área com esse nome (normalizado), criando se preciso."""
        pass

    @abstractmethod
    def ligar_area_equipe(self, equipe_id: int, area_id: int) -> bool:
        """Liga a área à equipe. False se já ligada."""
        pass

    @abstractmethod
    def ligar_area_pessoa(self, pessoa_id: int, area_id: int) -> bool:
        """Liga a área à pessoa. False se já ligada."""
        pass

    @abstractmethod
    def ligar_area_iniciativa(self, iniciativa_id: int, area_id: int) -> bool:
        """Liga a área à iniciativa. False se já ligada."""
        pass
