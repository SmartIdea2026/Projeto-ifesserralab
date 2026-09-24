"""Validacoes compartilhadas de extracao (US-002/US-003)."""

from collections import Counter


def slugs_duplicados(pessoas: list[dict]) -> dict[str, int]:
    contagem = Counter(p["slug"] for p in pessoas)
    return {slug: total for slug, total in contagem.items() if total > 1}


def validar_slugs_unicos(pessoas: list[dict], contexto: str) -> None:
    duplicados = slugs_duplicados(pessoas)
    if duplicados:
        raise ValueError(f"Slugs duplicados em {contexto}: {sorted(duplicados)}")
