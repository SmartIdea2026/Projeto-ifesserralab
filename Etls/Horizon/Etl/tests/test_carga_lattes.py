import json
from datetime import date, datetime

import pytest

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.lattes import CarregadorLattes, Curriculo, ler_curriculos

LATTES_ANA = "1111111111111111"
LATTES_BRUNO = "2222222222222222"


def _curriculo(lattes_id, nome, citacoes, atualizacao="15/03/2025", **secoes):
    dados = {
        "informacoes_pessoais": {
            "nome_completo": nome,
            "texto_resumo": f"Resumo de {nome}",
            "nome_citacoes": citacoes,
            "atualizacao_cv": atualizacao,
            "url": f"http://lattes.cnpq.br/{lattes_id}",
        }
    }
    dados.update(secoes)
    return Curriculo(f"/lattes/{lattes_id}.json", lattes_id, dados)


@pytest.fixture
def contexto(conexao_horizon):
    return ContextoCarga.criar(conexao_horizon)


def _consultar(conexao, consulta, parametros=()):
    with conexao.cursor() as cursor:
        cursor.execute(consulta, parametros)
        return cursor.fetchall()


def _participantes(conexao, nome_iniciativa):
    return _consultar(
        conexao,
        """
        SELECT pe.nome, pa.nome FROM participantes_iniciativa pi
        JOIN iniciativas i ON i.id = pi.iniciativa_id
        JOIN pessoas pe ON pe.id = pi.pessoa_id
        JOIN papeis pa ON pa.id = pi.papel_id
        WHERE i.nome = %s ORDER BY pa.nome, pe.nome
        """,
        (nome_iniciativa,),
    )


def test_dono_perfil_e_identificador(contexto, conexao_horizon):
    CarregadorLattes(contexto).carregar_pessoas(
        [_curriculo(LATTES_ANA, "Ana Souza", "SOUZA, A.;SOUZA, ANA")]
    )

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT p.nome, i.fonte, i.codigo, pl.resumo, pl.nomes_citacao, pl.atualizado_em
        FROM pessoas p
        JOIN identificadores_pessoa i ON i.pessoa_id = p.id
        JOIN perfis_lattes pl ON pl.pessoa_id = p.id
        """,
        )
        == [
            (
                "Ana Souza",
                "lattes",
                LATTES_ANA,
                "Resumo de Ana Souza",
                "SOUZA, A.;SOUZA, ANA",
                datetime(2025, 3, 15),
            )
        ]
    )


def test_dono_ja_existente_pelo_nome_recebe_o_lattes(contexto, conexao_horizon):
    contexto.casamento_pessoas.match_or_create("Ana Souza")

    CarregadorLattes(contexto).carregar_pessoas(
        [_curriculo(LATTES_ANA, "ANA SOUZA", "SOUZA, A.")]
    )

    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM pessoas") == [(1,)]
    assert _consultar(conexao_horizon, "SELECT codigo FROM identificadores_pessoa") == [
        (LATTES_ANA,)
    ]


def test_homonimo_com_outro_lattes_vira_pessoa_separada(contexto, conexao_horizon):
    CarregadorLattes(contexto).carregar_pessoas(
        [
            _curriculo(LATTES_ANA, "Ana Souza", "SOUZA, A."),
            _curriculo(LATTES_BRUNO, "Ana Souza", "SOUZA, A."),
        ]
    )

    assert _consultar(
        conexao_horizon,
        "SELECT p.nome, i.codigo FROM pessoas p "
        "JOIN identificadores_pessoa i ON i.pessoa_id = p.id ORDER BY i.codigo",
    ) == [("Ana Souza", LATTES_ANA), ("Ana Souza", LATTES_BRUNO)]
    assert [r.motivo for r in contexto.relatorio.revisoes] == [
        f"homônimo de pessoa com outro Lattes ({LATTES_ANA})"
    ]


def test_perfil_sem_data_de_atualizacao_e_pulado(contexto, conexao_horizon):
    CarregadorLattes(contexto).carregar_pessoas(
        [_curriculo(LATTES_ANA, "Ana Souza", "SOUZA, A.", atualizacao="")]
    )

    assert _consultar(conexao_horizon, "SELECT COUNT(*) FROM perfis_lattes") == [(0,)]
    assert _consultar(
        conexao_horizon, "SELECT COUNT(*) FROM identificadores_pessoa"
    ) == [(1,)]
    assert [p.motivo for p in contexto.relatorio.pendencias] == [
        "perfil Lattes sem data de atualização"
    ]


def test_premios_idiomas_vinculos_e_formacao(contexto, conexao_horizon):
    curriculo = _curriculo(
        LATTES_ANA,
        "Ana Souza",
        "SOUZA, A.",
        premios_titulos=[{"descricao": "Prêmio Jovem Pesquisador", "ano": "2020"}],
        idiomas=[
            {
                "idioma": "Inglês",
                "compreende": "Bem",
                "fala": "Razoavelmente",
                "le": "Bem",
                "escreve": "Pouco",
            }
        ],
        atuacao_profissional=[
            {
                "instituicao": "Instituto Federal do Espírito Santo",
                "ano_inicio": "2010",
                "ano_fim": "Atual",
                "vinculo": "Servidor Público",
            },
            {
                "instituicao": "Petrobras",
                "ano_inicio": "2005",
                "ano_fim": "2009",
                "vinculo": "Celetista",
            },
            {"instituicao": "Prefeitura Municipal da Serra", "ano_inicio": "2003"},
        ],
        formacao_academica=[
            {
                "tipo": "Doutorado em Informática",
                "nome_instituicao": "Universidade Federal do Espírito Santo",
                "ano_inicio": "2012",
                "ano_conclusao": "2016",
                "descricao": "Título: Tese sobre redes, Ano de obtenção: 2016. "
                "Orientador: Ivo Lima. Co-orientador: Júlia Melo.",
            },
            {"tipo": ""},
        ],
    )
    carregador = CarregadorLattes(contexto)

    carregador.carregar_pessoas([curriculo])
    carregador.carregar_curriculos([curriculo])

    assert _consultar(conexao_horizon, "SELECT titulo, ano FROM premios") == [
        ("Prêmio Jovem Pesquisador", 2020)
    ]
    assert _consultar(
        conexao_horizon,
        "SELECT i.nome, p.leitura, p.escrita, p.fala, p.compreensao "
        "FROM proficiencias p JOIN idiomas i ON i.id = p.idioma_id",
    ) == [("Inglês", "alto", "basico", "medio", "alto")]
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT o.nome, o.tipo, pa.nome, v.data_inicio, v.data_fim
        FROM vinculos v
        JOIN organizacoes o ON o.id = v.organizacao_id
        JOIN papeis pa ON pa.id = v.papel_id
        ORDER BY v.data_inicio
        """,
        )
        == [
            ("Petrobras", "empresa", "Celetista", date(2005, 1, 1), date(2009, 12, 31)),
            (
                "Instituto Federal do Espírito Santo",
                "instituicao_ensino",
                "Servidor Público",
                date(2010, 1, 1),
                None,
            ),
        ]
    )
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT t.nome, o.nome, f.curso, f.ano_inicio, f.ano_fim, f.titulo_tese
        FROM formacoes_academicas f
        JOIN tipos_formacao t ON t.id = f.tipo_formacao_id
        JOIN organizacoes o ON o.id = f.organizacao_id
        ORDER BY f.id
        """,
        )
        == [
            (
                "Doutorado",
                "Universidade Federal do Espírito Santo",
                "Informática",
                2012,
                2016,
                "Tese sobre redes",
            ),
            ("Unknown", "Unknown Institution", "Unknown", 0, None, None),
        ]
    )
    assert _consultar(
        conexao_horizon,
        "SELECT p.nome, o.papel FROM orientadores_formacao o "
        "JOIN pessoas p ON p.id = o.pessoa_id ORDER BY o.papel",
    ) == [("Júlia Melo", "coorientador"), ("Ivo Lima", "orientador")]
    assert [p.motivo for p in contexto.relatorio.pendencias] == [
        "atuação profissional sem tipo de vínculo"
    ]


def test_artigos_coautores_e_producao_tecnica(contexto, conexao_horizon):
    artigo = {
        "titulo": "Robótica na escola",
        "ano": "2023",
        "revista": "Revista Brasileira de Informática na Educação",
        "volume": "31",
        "paginas": "1-10",
        "doi": "10.5753/rbie.1",
        "autores": "SOUZA, A.; LIMA, B.; FULANO, X.",
    }
    ana = _curriculo(
        LATTES_ANA,
        "Ana Souza",
        "SOUZA, A.;SOUZA, ANA",
        producao_bibliografica={
            "artigos_periodicos": [artigo],
            "trabalhos_completos_congressos": [
                {"titulo": "Trabalho sem ano", "evento": None, "autores": "SOUZA, A."}
            ],
        },
        producao_tecnica={
            "softwares_sem_patente": [{"titulo": "Sistema Horizon", "ano": "2024"}]
        },
    )
    bruno = _curriculo(
        LATTES_BRUNO,
        "Bruno Lima",
        "LIMA, B.",
        producao_bibliografica={"artigos_periodicos": [artigo]},
    )
    carregador = CarregadorLattes(contexto)

    carregador.carregar_pessoas([ana, bruno])
    carregador.carregar_curriculos([ana, bruno])

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT t.nome, p.titulo, p.ano, a.veiculo, p.link
        FROM producoes p
        JOIN artigos a ON a.id = p.id
        JOIN tipos_producao t ON t.id = p.tipo_producao_id
        ORDER BY p.id
        """,
        )
        == [
            (
                "artigo",
                "Robótica na escola",
                2023,
                "Revista Brasileira de Informática na Educação",
                "https://doi.org/10.5753/rbie.1",
            ),
            (
                "trabalhos_completos_congressos",
                "Trabalho sem ano",
                0,
                "Não informado",
                None,
            ),
        ]
    )
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT pe.nome FROM autores_producao ap
        JOIN producoes p ON p.id = ap.producao_id
        JOIN pessoas pe ON pe.id = ap.pessoa_id
        WHERE p.titulo = 'Robótica na escola' ORDER BY pe.nome
        """,
        )
        == [("Ana Souza",), ("Bruno Lima",)]
    )
    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT t.nome, pe.nome FROM producoes p
        JOIN tipos_producao t ON t.id = p.tipo_producao_id
        JOIN autores_producao ap ON ap.producao_id = p.id
        JOIN pessoas pe ON pe.id = ap.pessoa_id
        WHERE p.titulo = 'Sistema Horizon'
        """,
        )
        == [("softwares_sem_patente", "Ana Souza")]
    )


def test_projetos_juntam_sem_sobrescrever_e_financiadora(contexto, conexao_horizon):
    projeto_sigpesq = contexto.iniciativas.criar(
        "Cidades Inteligentes",
        "projeto_pesquisa",
        contexto.organizacoes.ifes_id(),
        "em_andamento",
        "Resumo do SigPesq",
    )
    ana = _curriculo(
        LATTES_ANA,
        "Ana Souza",
        "SOUZA, A.",
        projetos_pesquisa=[
            {
                "nome": "Cidades Inteligentes",
                "ano_inicio": "2019",
                "ano_conclusao": "2021",
                "descricao": ["Descrição: Resumo do Lattes. Situação: Concluído;"],
                "integrantes": [
                    {"nome": "Ana Souza", "papel": "Coordenador"},
                    {"nome": "Carla Dias", "papel": "Integrante"},
                ],
            }
        ],
        projetos_extensao=[
            {
                "nome": "Robótica nas Escolas",
                "ano_inicio": "2022",
                "ano_conclusao": "Atual",
                "descricao": ["Descrição: Extensão. Situação: Em andamento;"],
                "integrantes": [
                    {"nome": "Ana Souza", "papel": "Coordenador"},
                    {"nome": "Davi Melo", "papel": "Estudante"},
                ],
                "financiadores": [{"nome": "FAPES"}],
            }
        ],
    )
    carregador = CarregadorLattes(contexto)

    carregador.carregar_pessoas([ana])
    carregador.carregar_curriculos([ana])

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT i.nome, t.nome, i.situacao, i.descricao, i.data_inicio, i.data_fim
        FROM iniciativas i JOIN tipos_iniciativa t ON t.id = i.tipo_iniciativa_id
        ORDER BY i.id
        """,
        )
        == [
            (
                "Cidades Inteligentes",
                "projeto_pesquisa",
                "em_andamento",
                "Resumo do SigPesq",
                date(2019, 1, 1),
                date(2021, 12, 31),
            ),
            (
                "Robótica nas Escolas",
                "projeto_extensao",
                "em_andamento",
                "Extensão",
                date(2022, 1, 1),
                None,
            ),
        ]
    )
    assert _participantes(conexao_horizon, "Cidades Inteligentes") == [
        ("Ana Souza", "coordenador"),
        ("Carla Dias", "pesquisador"),
    ]
    assert _participantes(conexao_horizon, "Robótica nas Escolas") == [
        ("Ana Souza", "coordenador"),
        ("Davi Melo", "estudante"),
    ]
    assert _consultar(
        conexao_horizon,
        "SELECT o.nome, o.tipo, oi.papel FROM organizacoes_iniciativa oi "
        "JOIN organizacoes o ON o.id = oi.organizacao_id",
    ) == [("FAPES", "fomento", "financiadora")]
    assert contexto.iniciativas.buscar(projeto_sigpesq).descricao == "Resumo do SigPesq"


def test_orientacoes_do_dono(contexto, conexao_horizon):
    ana = _curriculo(
        LATTES_ANA,
        "Ana Souza",
        "SOUZA, A.",
        orientacoes={
            "concluidas": {
                "mestrado": [
                    {
                        "titulo": "Dissertação sobre IoT",
                        "orientando": "Eduardo Reis",
                        "ano": "2019",
                        "natureza": "Dissertação de mestrado",
                    }
                ]
            },
            "em_andamento": {
                "iniciacao_cientifica": [
                    {
                        "titulo": "Plano de IC",
                        "orientando": "Fabiana Cruz",
                        "ano_inicio": "2024",
                    }
                ]
            },
        },
    )
    carregador = CarregadorLattes(contexto)

    carregador.carregar_pessoas([ana])
    carregador.carregar_orientacoes([ana])

    assert (
        _consultar(
            conexao_horizon,
            """
        SELECT i.nome, t.nome, i.situacao, o.sigla FROM iniciativas i
        JOIN tipos_iniciativa t ON t.id = i.tipo_iniciativa_id
        JOIN organizacoes o ON o.id = i.organizacao_id ORDER BY i.nome
        """,
        )
        == [
            ("Dissertação sobre IoT", "orientacao", "concluida", "IFES"),
            ("Plano de IC", "orientacao", "em_andamento", "IFES"),
        ]
    )
    assert _participantes(conexao_horizon, "Dissertação sobre IoT") == [
        ("Ana Souza", "orientador"),
        ("Eduardo Reis", "orientando"),
    ]


def test_ler_curriculos_da_pasta(tmp_path):
    (tmp_path / f"Ana_{LATTES_ANA}.json").write_text(
        json.dumps({"informacoes_pessoais": {"nome_completo": "Ana"}}), encoding="utf-8"
    )
    (tmp_path / "sem_id.json").write_text("{}", encoding="utf-8")
    (tmp_path / f"x_{LATTES_BRUNO}.json").write_text("{quebrado", encoding="utf-8")

    curriculos = ler_curriculos(str(tmp_path))

    assert [c.lattes_id for c in curriculos] == [LATTES_ANA]
