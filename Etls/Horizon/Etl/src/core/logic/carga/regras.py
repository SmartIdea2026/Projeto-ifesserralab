"""Regras de mapeamento das fontes para o banco Horizon, decididas na migração."""

from datetime import date, datetime
from typing import Any, Optional, Tuple, Union

import pandas as pd

from src.core.logic.initiative_identity import normalize_text

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


_MESES = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

_PAPEL_EQUIPE_CNPQ = {
    "pesquisador": "pesquisador",
    "estudante": "estudante",
    "tecnico": "tecnico",
    "lider": "lider",
}


def data_cnpq(valor: Any) -> Optional[date]:
    """Data do espelho do CNPq: "dd/mm/aaaa" ou "Anterior a <mês> de <ano>".

    Mesmas regras do CnpqSyncLogic antigo; mês não reconhecido vira janeiro.
    """
    texto_data = str(valor or "").strip()
    minusculo = texto_data.lower()
    if minusculo in ("", "não informada", "não informado", "n/a"):
        return None
    try:
        return datetime.strptime(texto_data, "%d/%m/%Y").date()
    except ValueError:
        pass
    if "anterior a" in minusculo:
        partes = minusculo.replace("anterior a", "").strip().split(" de ")
        if len(partes) == 2 and partes[1].strip().isdigit():
            return date(int(partes[1]), _MESES.get(partes[0].strip(), 1), 1)
    return None


def data_formacao_cnpq(valor: Any) -> Optional[date]:
    """Ano ou data de formação do grupo; ano sozinho vira 1º de janeiro."""
    texto_data = str(valor or "").strip()
    if len(texto_data) == 4 and texto_data.isdigit():
        return date(int(texto_data), 1, 1)
    return data_cnpq(texto_data)


def texto_cnpq(valor: Any) -> Optional[str]:
    """Texto de um campo do espelho do CNPq, que pode vir como dict ou lista."""
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor.strip() or None
    if isinstance(valor, dict):
        for chave in ("descricao", "descrição", "texto", "value"):
            aninhado = texto_cnpq(valor.get(chave))
            if aninhado:
                return aninhado
        partes = [texto_cnpq(item) for item in valor.values()]
    elif isinstance(valor, (list, tuple, set)):
        partes = [texto_cnpq(item) for item in valor]
    else:
        return str(valor).strip() or None
    partes = [parte for parte in partes if parte]
    return "\n".join(partes) if partes else None


def papel_equipe_cnpq(valor: Any) -> Tuple[Optional[str], bool]:
    """Papel fixo de equipe e se é egresso, a partir do papel do CNPq.

    "Pesquisador (Egresso)" vira ("pesquisador", True): o egresso é o papel base
    com data de fim (decisão 10). Papel fora do catálogo devolve (None, ...).
    """
    texto_papel = str(valor or "").strip() or "Pesquisador"
    egresso = "egresso" in texto_papel.lower()
    base = normalize_text(texto_papel.lower().replace("(egresso)", ""))
    return _PAPEL_EQUIPE_CNPQ.get(base), egresso
