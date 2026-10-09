"""Tipo de organização deduzido pelo nome, para instituições da atuação
profissional do Lattes (que podem ser escola, órgão público ou empresa)."""

from src.core.logic.initiative_identity import normalize_text

_TERMOS_ENSINO = ("universidade", "instituto", "faculdade", "escola", "centro federal")
_TERMOS_ORGAO_PUBLICO = ("prefeitura", "secretaria", "ministerio", "governo")


def tipo_organizacao_por_nome(nome: str) -> str:
    """instituicao_ensino, orgao_publico ou empresa, pelos termos do nome.

    Termos de ensino têm precedência (ex.: "Escola de Governo" é ensino).
    """
    texto = f" {normalize_text(nome)} "
    if any(f" {termo} " in texto for termo in _TERMOS_ENSINO):
        return "instituicao_ensino"
    if any(f" {termo} " in texto for termo in _TERMOS_ORGAO_PUBLICO):
        return "orgao_publico"
    return "empresa"
