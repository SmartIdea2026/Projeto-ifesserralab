"""Carga e normalizacao do Horizon via researchers_canonical.parquet (US-003)."""

import json
from pathlib import Path

from scripts.caminhos import RESEARCHERS_CANONICAL
from scripts.normalizacao import normalizar
from scripts.validacoes import validar_slugs_unicos

COLUNAS = ["name", "classification", "campus", "cnpq_url", "was_student", "was_staff"]


def _e_nulo(valor: str | bool | float | None) -> bool:
    return valor is None or (isinstance(valor, float) and valor != valor)


def _limpar(valor: str | bool | float | None) -> str | bool | None:
    return None if _e_nulo(valor) else valor


def parse_campus(valor: str | dict | float | None) -> str | None:
    if _e_nulo(valor):
        return None
    dado = json.loads(valor) if isinstance(valor, str) else valor
    if isinstance(dado, dict):
        nome = dado.get("name")
        return nome if isinstance(nome, str) and nome.strip() else None
    raise ValueError(f"Campus em formato inesperado: {valor!r}")


def carregar_horizon(
    arquivo_parquet: Path = RESEARCHERS_CANONICAL, ignorar_invalidos: bool = False
) -> tuple[list[dict], list[dict]]:
    import pandas as pd

    df = pd.read_parquet(arquivo_parquet, columns=COLUNAS)
    validos: list[dict] = []
    invalidos: list[dict] = []
    for i, linha in enumerate(df.itertuples(index=False)):
        nome = _limpar(linha.name)
        try:
            if not isinstance(nome, str) or not nome.strip():
                raise ValueError("nome vazio ou ausente")
            slug = normalizar(nome)
        except ValueError:
            if not ignorar_invalidos:
                raise ValueError(f"Registro {i} do Horizon com nome invalido: {nome!r}")
            invalidos.append(
                {
                    "linha": i,
                    "nome": nome if isinstance(nome, str) else None,
                    "classification": _limpar(linha.classification),
                    "campus_bruto": _limpar(linha.campus),
                }
            )
            continue
        validos.append(
            {
                "slug": slug,
                "nome": nome,
                "classification": _limpar(linha.classification),
                "campus": parse_campus(_limpar(linha.campus)),
                "cnpq_url": _limpar(linha.cnpq_url),
                "was_student": _limpar(linha.was_student),
                "was_staff": _limpar(linha.was_staff),
            }
        )
    validar_slugs_unicos(validos, "horizon")
    return validos, invalidos
