"""Normalizacao de nomes de pessoas em slugs kebab-case (US-001)."""

import re
import unicodedata

PARTICULAS = frozenset({"de", "da", "do", "das", "dos", "e"})


def normalizar(nome: str) -> str:
    """Converte um nome proprio em slug kebab-case (minusculas, sem acentos/caracteres especiais)."""
    if not isinstance(nome, str) or not nome.strip():
        raise ValueError("Nome vazio ou invalido: nao e possivel gerar slug.")
    texto = unicodedata.normalize("NFD", nome.strip().lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    if not texto:
        raise ValueError(f"Nome sem caracteres alfanumericos: {nome!r}")
    return texto


def contar_termos(slug: str) -> int:
    """Conta termos do slug, excluindo particulas (BR02); exige entrada ja normalizada."""
    if not isinstance(slug, str) or not slug.strip():
        raise ValueError("Slug vazio ou invalido: nao e possivel contar termos.")
    if re.search(r"\s", slug):
        raise ValueError(f"Entrada deve ser slug kebab-case, nao nome bruto: {slug!r}")
    termos = [t for t in slug.strip().split("-") if t and t not in PARTICULAS]
    return len(termos)
