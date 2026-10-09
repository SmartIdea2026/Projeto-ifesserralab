"""Liga o PersonMatcher ao repositório de pessoas.

O casamento de pessoas não muda (decisão 2): o PersonMatcher só precisa de um
controlador com ``get_all`` e ``create_person``, que aqui vêm do banco novo.
"""

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from src.core.ports.repositorio_pessoas import RepositorioPessoas


@dataclass
class PessoaParaCasamento:
    """Pessoa no formato que o PersonMatcher lê (nomes de atributo em inglês)."""

    id: int
    name: str
    emails: List[str] = field(default_factory=list)
    # Usados pelo PersonMatcher para preferir o registro mais completo.
    identification_id: Optional[str] = None
    resume: Optional[str] = None
    citation_names: Optional[str] = None
    cnpq_url: Optional[str] = None


class ControladorPessoasRepositorio:
    """Expõe ao PersonMatcher as duas operações que ele usa."""

    def __init__(self, repositorio: RepositorioPessoas):
        self._repositorio = repositorio

    def get_all(self) -> List[PessoaParaCasamento]:
        return [
            PessoaParaCasamento(
                id=pessoa.id,
                name=pessoa.nome,
                emails=list(pessoa.emails),
                cnpq_url=pessoa.identificadores.get("lattes"),
            )
            for pessoa in self._repositorio.listar()
        ]

    def create_person(
        self, name: str, emails: Optional[Iterable[str]] = None
    ) -> PessoaParaCasamento:
        emails = [email for email in (emails or []) if email]
        pessoa_id = self._repositorio.criar(name, emails)
        return PessoaParaCasamento(id=pessoa_id, name=name)
