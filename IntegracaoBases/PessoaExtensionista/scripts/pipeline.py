"""Cruzamento extensao x Horizon e geracao dos 5 JSONs de auditoria (US-004)."""

import json
from datetime import datetime
from pathlib import Path

from scripts.caminhos import OUTPUT
from scripts.extracao_extensao import contagens, extrair_pessoas_extensao
from scripts.extracao_horizon import carregar_horizon
from scripts.normalizacao import PARTICULAS, contar_termos
from scripts.validacoes import slugs_duplicados

BASELINE = {"total": 399, "catalogados": 342, "pontuais": 57}
MOTIVO_NOME_CURTO = {1: "nome_curto_1_termo", 2: "nome_curto_2_termos"}

EXPLICACAO_PONTUAIS = (
    "2 coordenadores de acao incluidos na fonte nova de acoes cruzam com o Horizon "
    "(alexander-jeferson-nassau-borges, livia-de-azevedo-silveira-rangel) e 1 match "
    "adicional entre pontuais; a decomposicao por classification da analise consolidada "
    "(27 alunos/22 servidores/8 externos) nao reproduz a classificacao real do parquet "
    "(34 alunos/23 servidores/2 externos/1 sem classificacao)"
)
EXPLICACAO_EXCLUSIVOS = (
    "consequencia direta do total de matches acima do baseline (universos fixos)"
)


def _bloco_sem_slug(pessoa: dict) -> dict:
    return {chave: valor for chave, valor in pessoa.items() if chave != "slug"}


def cruzar(extensao: list[dict], horizon: list[dict]) -> dict:
    dup_ext = slugs_duplicados(extensao)
    dup_hor = slugs_duplicados(horizon)
    if dup_ext or dup_hor:
        raise ValueError(
            "Cardinalidade 1:1 violada - slugs duplicados: "
            f"extensao={sorted(dup_ext)} horizon={sorted(dup_hor)}"
        )
    horizon_por_slug = {p["slug"]: p for p in horizon}
    matches = []
    for pessoa in extensao:
        alvo = horizon_por_slug.get(pessoa["slug"])
        if alvo is None:
            continue
        matches.append(
            {
                "slug": pessoa["slug"],
                "termo_count": contar_termos(pessoa["slug"]),
                "extensao": _bloco_sem_slug(pessoa),
                "horizon": _bloco_sem_slug(alvo),
            }
        )
    matches.sort(key=lambda m: m["slug"])
    confirmados = [m for m in matches if m["termo_count"] >= 3]
    a_validar = [
        {**m, "motivo": MOTIVO_NOME_CURTO.get(m["termo_count"], "nome_curto_sem_termo")}
        for m in matches
        if m["termo_count"] < 3
    ]
    slugs_match = {m["slug"] for m in matches}
    exclusivos_extensao = sorted(
        (p for p in extensao if p["slug"] not in slugs_match), key=lambda p: p["slug"]
    )
    exclusivos_horizon = sorted(
        (p for p in horizon if p["slug"] not in slugs_match), key=lambda p: p["slug"]
    )
    return {
        "confirmados": confirmados,
        "a_validar": a_validar,
        "exclusivos_extensao": exclusivos_extensao,
        "exclusivos_horizon": exclusivos_horizon,
    }


def _comparar_baseline(cruzamento: dict) -> list[dict]:
    todos_matches = cruzamento["confirmados"] + cruzamento["a_validar"]
    obtidos = {
        "total_matches": len(todos_matches),
        "matches_catalogados": sum(
            1 for m in todos_matches if m["extensao"]["tipo"] == "catalogado"
        ),
        "matches_pontuais": sum(
            1 for m in todos_matches if m["extensao"]["tipo"] == "pontual"
        ),
        "exclusivos_extensao": len(cruzamento["exclusivos_extensao"]),
        "exclusivos_horizon": len(cruzamento["exclusivos_horizon"]),
    }
    esperados = {
        "total_matches": BASELINE["total"],
        "matches_catalogados": BASELINE["catalogados"],
        "matches_pontuais": BASELINE["pontuais"],
        "exclusivos_extensao": 515,
        "exclusivos_horizon": 9689,
    }
    desvios = []
    for metrica, esperado in esperados.items():
        obtido = obtidos[metrica]
        if obtido != esperado:
            desvios.append(
                {
                    "metrica": metrica,
                    "esperado": esperado,
                    "obtido": obtido,
                    "diferenca": obtido - esperado,
                    "explicacao": (
                        EXPLICACAO_PONTUAIS
                        if metrica in ("total_matches", "matches_pontuais")
                        else EXPLICACAO_EXCLUSIVOS
                    ),
                }
            )
    return desvios


def auditar(
    extensao: list[dict],
    horizon: list[dict],
    invalidos_horizon: list[dict],
    cruzamento: dict,
) -> dict:
    cont = contagens(extensao)
    return {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "insumos": {
            "extensao_catalogados": " bases/SRC/api/extensionistas/index.json (757 registros)",
            "extensao_atividades": " bases/SRC/api/atividades/*.json (525 arquivos)",
            "extensao_acoes": " bases/SRC/api/acoes/*.json (202 arquivos)",
            "horizon_parquet": " bases/horizon/researchers_canonical.parquet",
        },
        "universos": {
            "extensao_total": cont["total"],
            "catalogados": cont["catalogados"],
            "pontuais": cont["pontuais"],
            "horizon_lidas": len(horizon) + len(invalidos_horizon),
            "horizon_validas": len(horizon),
            "horizon_invalidas": len(invalidos_horizon),
        },
        "cruzamento": {
            "matches_confirmados": len(cruzamento["confirmados"]),
            "matches_a_validar": len(cruzamento["a_validar"]),
            "exclusivos_extensao": len(cruzamento["exclusivos_extensao"]),
            "exclusivos_horizon": len(cruzamento["exclusivos_horizon"]),
        },
        "baseline_analise_consolidada": dict(BASELINE),
        "desvios": _comparar_baseline(cruzamento),
        "auditoria": {
            "slug_unico_extensao": not slugs_duplicados(extensao),
            "slug_unico_horizon": not slugs_duplicados(horizon),
            "cardinalidade_1_1": True,
            "particulas_excluidas": sorted(PARTICULAS),
            "registros_invalidos_horizon": invalidos_horizon,
        },
    }


def _escrever_json(caminho: Path, dado) -> None:
    caminho.write_text(
        json.dumps(dado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def gerar_outputs(pasta_saida: Path = OUTPUT) -> dict:
    extensao = extrair_pessoas_extensao()
    horizon, invalidos = carregar_horizon(ignorar_invalidos=True)
    resultado = cruzar(extensao, horizon)
    resumo = auditar(extensao, horizon, invalidos, resultado)
    pasta_saida.mkdir(parents=True, exist_ok=True)
    _escrever_json(pasta_saida / "matches_confirmados.json", resultado["confirmados"])
    _escrever_json(pasta_saida / "matches_a_validar.json", resultado["a_validar"])
    _escrever_json(pasta_saida / "exclusivos_extensao.json", resultado["exclusivos_extensao"])
    _escrever_json(pasta_saida / "exclusivos_horizon.json", resultado["exclusivos_horizon"])
    _escrever_json(pasta_saida / "resumo_auditoria.json", resumo)
    return resumo


if __name__ == "__main__":
    resumo = gerar_outputs()
    print(json.dumps(resumo["cruzamento"], ensure_ascii=False, indent=2))
    desvios = resumo["desvios"]
    if not desvios:
        print("desvios vs baseline da analise: nenhum")
    else:
        print("desvios vs baseline da analise:")
        for d in desvios:
            print(f"  {d['metrica']}: esperado={d['esperado']} obtido={d['obtido']} ({d['diferenca']:+d})")
