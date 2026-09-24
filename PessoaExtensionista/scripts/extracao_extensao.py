"""Extracao das 914 pessoas da extensao a partir de bases/SRC (US-002)."""

import json
from pathlib import Path

from scripts.caminhos import ACOES, ATIVIDADES, EXTENSIONISTAS_INDEX
from scripts.normalizacao import normalizar
from scripts.validacoes import validar_slugs_unicos

ORIGEM_EXTENSAO = ["SRC", "DIRETORIA"]


def _caminhos_src(raiz_src: Path | None) -> tuple[Path, Path, Path]:
    if raiz_src is None:
        return EXTENSIONISTAS_INDEX, ATIVIDADES, ACOES
    return (
        raiz_src / "api" / "extensionistas" / "index.json",
        raiz_src / "api" / "atividades",
        raiz_src / "api" / "acoes",
    )


def _registro_extensao(
    slug: str,
    nome: str,
    tipo: str,
    *,
    funcoes: list[str] | None = None,
    anos: list[str] | None = None,
    coordena: int | None = None,
    equipe: int | None = None,
    imp_coord: int | None = None,
    imp_eq: int | None = None,
    impacto: int | None = None,
    atividades: list[str] | None = None,
    acoes: list[str] | None = None,
) -> dict:
    return {
        "slug": slug,
        "nome": nome,
        "origem": list(ORIGEM_EXTENSAO),
        "tipo": tipo,
        "funcoes": funcoes if funcoes is not None else [],
        "anos": anos,
        "coordena": coordena,
        "equipe": equipe,
        "imp_coord": imp_coord,
        "imp_eq": imp_eq,
        "impacto": impacto,
        "atividades": atividades,
        "acoes": acoes,
    }


def _registro_catalogado(item: dict) -> dict:
    return _registro_extensao(
        normalizar(item["nome"]),
        item["nome"],
        "catalogado",
        funcoes=list(item.get("funcoes") or []),
        anos=list(item.get("anos") or []),
        coordena=item.get("coordena"),
        equipe=item.get("equipe"),
        imp_coord=item.get("imp_coord"),
        imp_eq=item.get("imp_eq"),
        impacto=item.get("impacto"),
    )


def extrair_catalogados(arquivo_index: Path = EXTENSIONISTAS_INDEX) -> list[dict]:
    itens = json.loads(arquivo_index.read_text(encoding="utf-8"))
    pessoas = [_registro_catalogado(item) for item in itens]
    validar_slugs_unicos(pessoas, "extensao (catalogados)")
    return pessoas


def _pessoas_da_atividade(conteudo: dict) -> list[tuple[str, str | None]]:
    pessoas: list[tuple[str, str | None]] = []
    coordenador = conteudo.get("coordenador_acao")
    if isinstance(coordenador, str) and coordenador.strip():
        pessoas.append((coordenador.strip(), None))
    for membro in conteudo.get("equipe_execucao") or []:
        membro = membro or {}
        nome = membro.get("nome")
        if isinstance(nome, str) and nome.strip():
            funcao = membro.get("funcao")
            funcao_limpa = funcao.strip() if isinstance(funcao, str) and funcao.strip() else None
            pessoas.append((nome.strip(), funcao_limpa))
    return pessoas


def extrair_pontuais(
    slugs_catalogados: set[str],
    raiz_atividades: Path = ATIVIDADES,
    coordenacoes: dict[str, dict] | None = None,
) -> list[dict]:
    nomes: dict[str, str] = {}
    funcoes: dict[str, set[str]] = {}
    atividades: dict[str, set[str]] = {}

    for arquivo in sorted(raiz_atividades.glob("*.json")):
        conteudo = json.loads(arquivo.read_text(encoding="utf-8"))
        atividade_id = conteudo.get("atividade_id")
        for nome, funcao in _pessoas_da_atividade(conteudo):
            slug = normalizar(nome)
            if slug in slugs_catalogados:
                continue
            nomes.setdefault(slug, nome)
            if funcao is not None:
                funcoes.setdefault(slug, set()).add(funcao)
            atividades.setdefault(slug, set()).add(atividade_id)

    pessoas = []
    for slug in sorted(nomes):
        acoes = sorted(coordenacoes[slug]["acoes"]) if slug in (coordenacoes or {}) else None
        pessoas.append(
            _registro_extensao(
                slug,
                nomes[slug],
                "pontual",
                funcoes=sorted(funcoes.get(slug, set())),
                atividades=sorted(atividades.get(slug, set())),
                acoes=acoes,
            )
        )
    validar_slugs_unicos(pessoas, "extensao (pontuais)")
    return pessoas


def extrair_coordenacoes_acoes(raiz_acoes: Path = ACOES) -> dict[str, dict]:
    coordenacoes: dict[str, dict] = {}
    for arquivo in sorted(raiz_acoes.glob("*.json")):
        acao = json.loads(arquivo.read_text(encoding="utf-8"))
        if not isinstance(acao, dict):
            continue
        coordenador = acao.get("Coordenador(a)") or acao.get("coordenador")
        if isinstance(coordenador, str) and coordenador.strip():
            acao_id = acao.get("acao_id")
            if acao_id is not None:
                slug = normalizar(coordenador.strip())
                info = coordenacoes.setdefault(slug, {"nome": coordenador.strip(), "acoes": set()})
                info["acoes"].add(acao_id)
    return coordenacoes


def _aplicar_acoes(pessoas: list[dict], coordenacoes: dict[str, dict]) -> None:
    for pessoa in pessoas:
        info = coordenacoes.get(pessoa["slug"])
        pessoa["acoes"] = sorted(info["acoes"]) if info else None


def _pessoas_so_acoes(
    coordenacoes: dict[str, dict], slugs_conhecidos: set[str]
) -> list[dict]:
    pessoas = []
    for slug in sorted(coordenacoes):
        if slug in slugs_conhecidos:
            continue
        info = coordenacoes[slug]
        pessoas.append(
            _registro_extensao(
                slug,
                info["nome"],
                "pontual",
                atividades=None,
                acoes=sorted(info["acoes"]),
            )
        )
    return pessoas


def extrair_pessoas_extensao(raiz_src: Path | None = None) -> list[dict]:
    arquivo_index, pasta_atividades, pasta_acoes = _caminhos_src(raiz_src)
    coordenacoes = extrair_coordenacoes_acoes(pasta_acoes)
    catalogados = extrair_catalogados(arquivo_index)
    _aplicar_acoes(catalogados, coordenacoes)
    slugs_conhecidos = {p["slug"] for p in catalogados}
    pontuais = extrair_pontuais(slugs_conhecidos, pasta_atividades, coordenacoes)
    slugs_conhecidos.update(p["slug"] for p in pontuais)
    novos = _pessoas_so_acoes(coordenacoes, slugs_conhecidos)
    pessoas = catalogados + pontuais + novos
    validar_slugs_unicos(pessoas, "extensao")
    return pessoas


def contagens(pessoas: list[dict]) -> dict[str, int]:
    return {
        "total": len(pessoas),
        "catalogados": sum(1 for p in pessoas if p["tipo"] == "catalogado"),
        "pontuais": sum(1 for p in pessoas if p["tipo"] == "pontual"),
    }
