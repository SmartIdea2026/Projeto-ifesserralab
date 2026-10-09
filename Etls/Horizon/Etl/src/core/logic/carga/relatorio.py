"""Relatório da carga no banco Horizon: o que foi gravado e o que ficou de fora.

Não guarda e-mails: só o passo, o motivo e uma descrição curta do registro.
"""

import os
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, DefaultDict, Dict, List

from src.core.logic.atomic_io import atomic_write_json

PASTA_PADRAO = "data/reports"
NOME_ARQUIVO = "carga_postgres"


@dataclass
class Pendencia:
    """Registro que não foi gravado (ou foi gravado em parte) e o motivo."""

    passo: str
    motivo: str
    registro: str


class RelatorioCarga:
    def __init__(self) -> None:
        self.inicio = datetime.now()
        self.pendencias: List[Pendencia] = []
        self._contagens: DefaultDict[str, Counter] = defaultdict(Counter)

    def contar(self, passo: str, evento: str, quantidade: int = 1) -> None:
        self._contagens[passo][evento] += quantidade

    def pular(self, passo: str, motivo: str, registro: str) -> None:
        """Registro deixado de fora (dado obrigatório ausente, erro ao gravar...)."""
        self.pendencias.append(Pendencia(passo, motivo, registro))
        self.contar(passo, "pulados")

    def descartar(self, passo: str, campo: str, quantidade: int = 1) -> None:
        """Campo lido da fonte que não tem destino no banco (decisão 9)."""
        self.contar(passo, f"descartado:{campo}", quantidade)

    def contagens(self) -> Dict[str, Dict[str, int]]:
        return {passo: dict(eventos) for passo, eventos in self._contagens.items()}

    def resumo(self) -> Dict[str, Any]:
        return {
            "inicio": self.inicio.isoformat(timespec="seconds"),
            "fim": datetime.now().isoformat(timespec="seconds"),
            "contagens": self.contagens(),
            "pendencias": [asdict(p) for p in self.pendencias],
        }

    def salvar(self, pasta: str = PASTA_PADRAO) -> str:
        """Grava o relatório com data e hora no nome e atualiza a cópia mais recente."""
        dados = self.resumo()
        carimbo = self.inicio.strftime("%Y%m%d_%H%M%S")
        caminho = os.path.join(pasta, f"{NOME_ARQUIVO}_{carimbo}.json")
        atomic_write_json(caminho, dados)
        atomic_write_json(os.path.join(pasta, f"{NOME_ARQUIVO}.json"), dados)
        return caminho
