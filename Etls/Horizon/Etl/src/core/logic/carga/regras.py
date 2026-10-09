"""Regras de mapeamento das fontes para o banco Horizon, decididas na migração."""

from datetime import date, datetime
from typing import Any, Optional, Union

import pandas as pd

Data = Union[date, datetime]

# Situações que as estratégias de mapeamento e o parser do Lattes produzem.
_SITUACAO_POR_STATUS = {
    "active": "em_andamento",
    "in progress": "em_andamento",
    "concluded": "concluida",
    "cancelled": "cancelada",
    "unknown": "desconhecida",
}

_NIVEL_POR_TERMO_LATTES = {
    "bem": "alto",
    "razoavelmente": "medio",
    "pouco": "basico",
}

_FORMATOS_DATA_LATTES = ("%d/%m/%Y", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d")


def _como_data(valor: Optional[Data]) -> Optional[date]:
    return valor.date() if isinstance(valor, datetime) else valor


def situacao_pela_data(data_fim: Optional[Data], hoje: Optional[date] = None) -> str:
    """Regra de projeto aprovado: fim no passado é concluída; sem fim ou futuro, em andamento."""
    fim = _como_data(data_fim)
    if fim is not None and fim < (hoje or date.today()):
        return "concluida"
    return "em_andamento"


def situacao_iniciativa(
    status: Any, data_fim: Optional[Data] = None, hoje: Optional[date] = None
) -> str:
    """Situação em português a partir do status das estratégias de mapeamento.

    Variações do parecer "aprovado" (ex.: "Aprovado com ressalvas") seguem a
    regra da data; status vazio ou desconhecido vira ``desconhecida``.
    """
    chave = str(status or "").strip().lower()
    if chave in _SITUACAO_POR_STATUS:
        return _SITUACAO_POR_STATUS[chave]
    if "aprovado" in chave:
        return situacao_pela_data(data_fim, hoje)
    return "desconhecida"


def nivel_proficiencia(valor: Any) -> str:
    """Nível de proficiência a partir do termo do Lattes (Bem, Razoavelmente, Pouco)."""
    return _NIVEL_POR_TERMO_LATTES.get(
        str(valor or "").strip().lower(), "nao_se_aplica"
    )


def inicio_do_ano(ano: Optional[int]) -> Optional[date]:
    """1º de janeiro do ano, como já é feito com os projetos do Lattes."""
    return date(ano, 1, 1) if ano else None


def fim_do_ano(ano: Optional[int]) -> Optional[date]:
    """31 de dezembro do ano."""
    return date(ano, 12, 31) if ano else None


def data_atualizacao_lattes(valor: Any) -> Optional[datetime]:
    """Data de atualização do currículo (``atualizacao_cv``), ou None se não houver."""
    if isinstance(valor, datetime):
        return valor
    texto = str(valor or "").strip()
    for formato in _FORMATOS_DATA_LATTES:
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return None


def texto(valor: Any) -> Optional[str]:
    """Texto limpo da planilha; vazio, None ou NaN viram None."""
    if valor is None:
        return None
    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass
    limpo = str(valor).strip()
    return limpo or None
