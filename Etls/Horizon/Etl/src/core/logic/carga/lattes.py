"""Carga dos currículos Lattes (JSON do scriptLattes) no banco Horizon.

Três fases, para que o casamento não dependa da ordem dos arquivos:

1. ``carregar_pessoas``: dono de cada currículo (pelo ID Lattes e, sem ele,
   pelo nome) e perfil Lattes;
2. ``carregar_curriculos``: prêmios, idiomas, vínculos (atuação profissional),
   formação com orientadores, artigos com coautores, produção técnica e projetos;
3. ``carregar_orientacoes``: orientações do dono do currículo.

Regras mantidas do ETL antigo: mapeamento do LattesParser e das estratégias
LattesProjectMappingStrategy/LattesAdvisorshipMappingStrategy; artigo casado
por DOI e depois título + ano; formação com valores genéricos quando falta dado;
orientador da formação lido da descrição; projeto repetido no currículo ignorado.

Decisões da migração aplicadas aqui:

* homônimo com outro ID Lattes vira pessoa separada e vai para revisão;
* perfil Lattes sem resumo, nomes de citação ou data de atualização é pulado;
* proficiência em alto/medio/basico/nao_se_aplica;
* vínculo com papel = tipo de vínculo do Lattes (sem ele, pulado) e tipo da
  organização pela regra do nome;
* coautores de artigos só quando casam com pessoa já existente (nome ou nome
  de citação, sem ambiguidade);
* ano ausente vira 0 e veículo ausente vira "Não informado";
* tipo do projeto vem do Lattes (pesquisa, extensão, desenvolvimento), no IFES;
* projeto/orientação com a mesma identidade ou o mesmo nome é juntado: só
  acrescenta participantes e preenche campos vazios;
* primeiro financiador do projeto vira organização financiadora (fomento).
"""

import glob
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from src.adapters.sources.lattes_parser import LattesParser
from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.regras import (
    data_atualizacao_lattes,
    fim_do_ano,
    inicio_do_ano,
    nivel_proficiencia,
    situacao_iniciativa,
    texto,
)
from src.core.logic.initiative_identity import normalize_text
from src.core.logic.strategies.lattes_advisorships import (
    LattesAdvisorshipMappingStrategy,
)
from src.core.logic.strategies.lattes_projects import LattesProjectMappingStrategy
from src.core.logic.tipo_organizacao import tipo_organizacao_por_nome
from src.core.ports.repositorio_producoes import (
    ANO_NAO_INFORMADO,
    TIPO_ARTIGO,
    TIPO_TRABALHO_CONGRESSO,
    VEICULO_NAO_INFORMADO,
)

PASSO_PESSOAS = "lattes_pessoas"
PASSO_CURRICULOS = "lattes_curriculos"
PASSO_ORIENTACOES = "lattes_orientacoes"
PASTA_PADRAO = "data/lattes_json"

TIPO_POR_LATTES = {
    "Research Project": "projeto_pesquisa",
    "Extension Project": "projeto_extensao",
    "Development Project": "projeto_desenvolvimento",
}
TIPOS_PROJETO = tuple(TIPO_POR_LATTES.values())
TIPO_ORIENTACAO = "orientacao"

# Valores genéricos da formação, mantidos como no ETL antigo.
INSTITUICAO_DESCONHECIDA = "Unknown Institution"
GRAU_DESCONHECIDO = "Unknown"
CURSO_SEM_TITULO = "Untitled"

_ORIENTADOR = re.compile(r"Orientador:\s*([^.;)]+)", re.IGNORECASE)
_COORIENTADOR = re.compile(r"Co-?orientador:\s*([^.;)]+)", re.IGNORECASE)


@dataclass
class Curriculo:
    caminho: str
    lattes_id: str
    dados: dict


def ler_curriculos(pasta: str = PASTA_PADRAO) -> List[Curriculo]:
    """JSONs da pasta cujo nome termina no ID Lattes (``..._<id>.json``)."""
    curriculos = []
    for caminho in sorted(glob.glob(os.path.join(pasta, "*.json"))):
        lattes_id = os.path.basename(caminho)[: -len(".json")].split("_")[-1]
        if not lattes_id.isdigit():
            continue
        try:
            with open(caminho, encoding="utf-8") as arquivo:
                curriculos.append(Curriculo(caminho, lattes_id, json.load(arquivo)))
        except (OSError, json.JSONDecodeError):
            continue
    return curriculos


class CarregadorLattes:
    def __init__(self, contexto: ContextoCarga, parser: Optional[LattesParser] = None):
        self._ctx = contexto
        self._parser = parser or LattesParser()
        self._donos: Dict[str, Tuple[int, str]] = {}
        self._por_identidade: Dict[str, int] = {}
        self._papeis: Dict[str, int] = {}
        self._coautores: Dict[str, int] = {}

    def carregar(self, curriculos: List[Curriculo]) -> None:
        self.carregar_pessoas(curriculos)
        self.carregar_curriculos(curriculos)
        self.carregar_orientacoes(curriculos)

    # ------------------------------------------------------------ fase 1
    def carregar_pessoas(self, curriculos: Iterable[Curriculo]) -> None:
        with self._ctx.passo(PASSO_PESSOAS):
            lattes_por_pessoa = {
                pessoa.id: pessoa.identificadores["lattes"]
                for pessoa in self._ctx.pessoas.listar()
                if "lattes" in pessoa.identificadores
            }
            for curriculo in curriculos:
                resultado: Dict[str, Tuple[int, str]] = {}
                with self._ctx.registro(PASSO_PESSOAS, f"Lattes {curriculo.lattes_id}"):
                    resultado["dono"] = self._dono(curriculo, lattes_por_pessoa)
                if "dono" in resultado:
                    self._donos[curriculo.lattes_id] = resultado["dono"]
                    lattes_por_pessoa[resultado["dono"][0]] = curriculo.lattes_id

    def _dono(
        self, curriculo: Curriculo, lattes_por_pessoa: Dict[int, str]
    ) -> Tuple[int, str]:
        dados = curriculo.dados
        info = self._parser.parse_personal_info(dados)
        nome = (
            texto(info.get("name"))
            or texto(dados.get("nome"))
            or texto((dados.get("informacoes_pessoais") or {}).get("nome_completo"))
        )

        pessoa_id = self._ctx.pessoas.buscar_por_identificador(
            "lattes", curriculo.lattes_id
        )
        if pessoa_id is None:
            if not nome:
                raise ValueError("currículo sem nome")
            pessoa = self._ctx.casamento_pessoas.match_or_create(
                nome, strict_match=True
            )
            if pessoa is None:
                raise ValueError("não foi possível criar a pessoa")
            pessoa_id = pessoa.id
            nome = pessoa.name or nome
            outro_lattes = lattes_por_pessoa.get(pessoa_id)
            if outro_lattes and outro_lattes != curriculo.lattes_id:
                pessoa_id = self._ctx.pessoas.criar(nome)
                self._ctx.relatorio.revisar(
                    PASSO_PESSOAS,
                    f"homônimo de pessoa com outro Lattes ({outro_lattes})",
                    f"{nome} ({curriculo.lattes_id})",
                )
            self._ctx.pessoas.definir_identificador(
                pessoa_id, "lattes", curriculo.lattes_id
            )
        self._ctx.relatorio.contar(PASSO_PESSOAS, "donos")
        self._perfil(pessoa_id, info, nome or curriculo.lattes_id)
        return pessoa_id, nome or curriculo.lattes_id

    def _perfil(self, pessoa_id: int, info: dict, nome: str) -> None:
        resumo = texto(info.get("resume"))
        citacao = texto(info.get("citation_names"))
        atualizado_em = data_atualizacao_lattes(info.get("updated_at"))
        faltando = [
            campo
            for campo, valor in (
                ("resumo", resumo),
                ("nomes de citação", citacao),
                ("data de atualização", atualizado_em),
            )
            if not valor
        ]
        if faltando:
            self._ctx.relatorio.pular(
                PASSO_PESSOAS, f"perfil Lattes sem {', '.join(faltando)}", nome
            )
            return
        self._ctx.pessoas.salvar_perfil_lattes(
            pessoa_id, resumo, citacao, atualizado_em
        )
        self._ctx.relatorio.contar(PASSO_PESSOAS, "perfis")

    # ------------------------------------------------------------ fase 2
    def carregar_curriculos(self, curriculos: Iterable[Curriculo]) -> None:
        with self._ctx.passo(PASSO_CURRICULOS):
            self._ifes_id = self._ctx.organizacoes.ifes_id()
            self._garantir_papeis("coordenador", "pesquisador", "estudante")
            self._coautores = self._indice_coautores()
            for curriculo in curriculos:
                dono = self._donos.get(curriculo.lattes_id)
                if dono is None:
                    self._ctx.relatorio.pular(
                        PASSO_CURRICULOS,
                        "dono do currículo não carregado",
                        curriculo.lattes_id,
                    )
                    continue
                self._premios(curriculo, *dono)
                self._idiomas(curriculo, *dono)
                self._vinculos(curriculo, *dono)
                self._formacoes(curriculo, *dono)
                self._artigos(curriculo, *dono)
                self._producoes_tecnicas(curriculo, *dono)
                self._projetos(curriculo, *dono)

    def _premios(self, curriculo: Curriculo, pessoa_id: int, nome: str) -> None:
        for premio in self._parser.parse_awards(curriculo.dados):
            with self._ctx.registro(PASSO_CURRICULOS, f"prêmio de {nome}"):
                if self._ctx.pessoas.adicionar_premio(
                    pessoa_id, premio["title"], premio.get("year")
                ):
                    self._ctx.relatorio.contar(PASSO_CURRICULOS, "premios")

    def _idiomas(self, curriculo: Curriculo, pessoa_id: int, nome: str) -> None:
        for idioma in self._parser.parse_languages(curriculo.dados):
            with self._ctx.registro(PASSO_CURRICULOS, f"idioma de {nome}"):
                if self._ctx.pessoas.definir_proficiencia(
                    pessoa_id,
                    idioma["language"],
                    nivel_proficiencia(idioma.get("reading")),
                    nivel_proficiencia(idioma.get("writing")),
                    nivel_proficiencia(idioma.get("speaking")),
                    nivel_proficiencia(idioma.get("comprehension")),
                ):
                    self._ctx.relatorio.contar(PASSO_CURRICULOS, "proficiencias")

    def _vinculos(self, curriculo: Curriculo, pessoa_id: int, nome: str) -> None:
        for atuacao in self._parser.parse_professional_activities(curriculo.dados):
            instituicao = atuacao["institution"]
            tipo_vinculo = texto(atuacao.get("bond"))
            if not tipo_vinculo:
                self._ctx.relatorio.pular(
                    PASSO_CURRICULOS,
                    "atuação profissional sem tipo de vínculo",
                    f"{instituicao} ({nome})",
                )
                continue
            with self._ctx.registro(PASSO_CURRICULOS, f"vínculo de {nome}"):
                organizacao_id = self._ctx.organizacoes.garantir_organizacao(
                    instituicao, tipo_organizacao_por_nome(instituicao)
                )
                papel_id = self._ctx.organizacoes.garantir_papel(
                    tipo_vinculo, "vinculo"
                )
                if self._ctx.organizacoes.adicionar_vinculo(
                    pessoa_id,
                    organizacao_id,
                    papel_id,
                    inicio_do_ano(atuacao.get("start_year")),
                    fim_do_ano(atuacao.get("end_year")),
                ):
                    self._ctx.relatorio.contar(PASSO_CURRICULOS, "vinculos")
                self._ctx.relatorio.descartar(
                    PASSO_CURRICULOS, "detalhes_da_atuacao_profissional"
                )

    def _formacoes(self, curriculo: Curriculo, pessoa_id: int, nome: str) -> None:
        for formacao in self._parser.parse_academic_education(curriculo.dados):
            with self._ctx.registro(PASSO_CURRICULOS, f"formação de {nome}"):
                organizacao_id = self._ctx.organizacoes.garantir_organizacao(
                    texto(formacao.get("institution")) or INSTITUICAO_DESCONHECIDA,
                    "instituicao_ensino",
                )
                tipo_id = self._ctx.formacoes.garantir_tipo_formacao(
                    texto(formacao.get("degree")) or GRAU_DESCONHECIDO
                )
                formacao_id, criada = self._ctx.formacoes.adicionar_formacao(
                    pessoa_id,
                    tipo_id,
                    organizacao_id,
                    texto(formacao.get("course_name")) or CURSO_SEM_TITULO,
                    formacao.get("start_year") or 0,
                    formacao.get("end_year"),
                    texto(formacao.get("thesis_title")),
                )
                if criada:
                    self._ctx.relatorio.contar(PASSO_CURRICULOS, "formacoes")
                descricao = str(formacao.get("description") or "")
                for padrao, papel in (
                    (_ORIENTADOR, "orientador"),
                    (_COORIENTADOR, "coorientador"),
                ):
                    encontrado = padrao.search(descricao)
                    if not encontrado:
                        continue
                    orientador = self._ctx.casamento_pessoas.match_or_create(
                        encontrado.group(1).strip(), strict_match=True
                    )
                    if orientador is not None:
                        self._ctx.formacoes.adicionar_orientador(
                            formacao_id, orientador.id, papel
                        )

    def _artigos(self, curriculo: Curriculo, pessoa_id: int, nome: str) -> None:
        artigos = self._parser.parse_articles(curriculo.dados)
        artigos += self._parser.parse_conference_papers(curriculo.dados)
        for artigo in artigos:
            titulo = texto(artigo.get("title"))
            if not titulo:
                self._ctx.relatorio.pular(PASSO_CURRICULOS, "artigo sem título", nome)
                continue
            with self._ctx.registro(PASSO_CURRICULOS, f"artigo de {nome}"):
                artigo_id, criado = self._ctx.producoes.garantir_artigo(
                    titulo,
                    artigo.get("year") or ANO_NAO_INFORMADO,
                    texto(artigo.get("journal_conference")) or VEICULO_NAO_INFORMADO,
                    tipo=(
                        TIPO_ARTIGO
                        if artigo.get("type") == "Journal"
                        else TIPO_TRABALHO_CONGRESSO
                    ),
                    volume=texto(artigo.get("volume")),
                    paginas=texto(artigo.get("pages")),
                    doi=texto(artigo.get("doi")),
                )
                if criado:
                    self._ctx.relatorio.contar(PASSO_CURRICULOS, "artigos")
                self._ctx.producoes.adicionar_autor(artigo_id, pessoa_id)
                for coautor in self._casar_coautores(artigo.get("authors_str")):
                    if coautor != pessoa_id and self._ctx.producoes.adicionar_autor(
                        artigo_id, coautor
                    ):
                        self._ctx.relatorio.contar(PASSO_CURRICULOS, "coautores")

    def _producoes_tecnicas(
        self, curriculo: Curriculo, pessoa_id: int, nome: str
    ) -> None:
        for producao in self._parser.parse_technical_productions(curriculo.dados):
            with self._ctx.registro(PASSO_CURRICULOS, f"produção técnica de {nome}"):
                producao_id, criada = self._ctx.producoes.garantir_producao(
                    producao["title"],
                    producao.get("year") or ANO_NAO_INFORMADO,
                    producao["production_type"],
                )
                if criada:
                    self._ctx.relatorio.contar(PASSO_CURRICULOS, "producoes_tecnicas")
                self._ctx.producoes.adicionar_autor(producao_id, pessoa_id)

    def _projetos(self, curriculo: Curriculo, pessoa_id: int, nome: str) -> None:
        projetos = self._parser.parse_research_projects(curriculo.dados)
        projetos += self._parser.parse_extension_projects(curriculo.dados)
        projetos += self._parser.parse_development_projects(curriculo.dados)

        unicos, vistos = [], set()
        for projeto in projetos:
            titulo = (projeto.get("name") or "").strip()
            if titulo and titulo not in vistos:
                projeto["name"] = titulo
                unicos.append(projeto)
                vistos.add(titulo)

        estrategia = LattesProjectMappingStrategy(
            nome, {p["name"]: p.get("role") for p in unicos}
        )
        for projeto in unicos:
            dados = estrategia.map_row(projeto)
            identidades: Dict[str, int] = {}
            gravado = False
            with self._ctx.registro(PASSO_CURRICULOS, f"projeto {projeto['name']}"):
                self._projeto(dados, projeto, identidades)
                gravado = True
            if gravado:
                self._por_identidade.update(identidades)

    def _projeto(self, dados: dict, projeto: dict, identidades: Dict[str, int]) -> None:
        metadados = dados.get("metadata") or {}
        tipo = TIPO_POR_LATTES.get(
            metadados.get("initiative_type_name"), "projeto_pesquisa"
        )
        projeto_id = self._gravar_juntando(
            PASSO_CURRICULOS,
            dados,
            tipo,
            TIPOS_PROJETO,
            identidades,
        )

        inicio = dados.get("start_date")
        self._participante(
            projeto_id, dados.get("coordinator_name"), "coordenador", inicio
        )
        for nome in dados.get("researcher_names") or []:
            self._participante(projeto_id, nome, "pesquisador", inicio)
        for nome in dados.get("student_names") or []:
            self._participante(projeto_id, nome, "estudante", inicio)

        financiador = texto(metadados.get("external_partner"))
        if financiador:
            organizacao_id = self._ctx.organizacoes.garantir_organizacao(
                financiador, "fomento"
            )
            self._ctx.iniciativas.ligar_organizacao(
                projeto_id, organizacao_id, "financiadora"
            )

    # ------------------------------------------------------------ fase 3
    def carregar_orientacoes(self, curriculos: Iterable[Curriculo]) -> None:
        with self._ctx.passo(PASSO_ORIENTACOES):
            self._ifes_id = self._ctx.organizacoes.ifes_id()
            self._garantir_papeis("orientador", "orientando")
            for curriculo in curriculos:
                dono = self._donos.get(curriculo.lattes_id)
                if dono is None:
                    self._ctx.relatorio.pular(
                        PASSO_ORIENTACOES,
                        "dono do currículo não carregado",
                        curriculo.lattes_id,
                    )
                    continue
                pessoa_id, nome = dono
                estrategia = LattesAdvisorshipMappingStrategy(nome)
                for orientacao in self._parser.parse_advisorships(curriculo.dados):
                    dados = estrategia.map_row(orientacao)
                    identidades: Dict[str, int] = {}
                    gravado = False
                    with self._ctx.registro(
                        PASSO_ORIENTACOES, f"orientação {dados.get('title')}"
                    ):
                        self._orientacao(dados, pessoa_id, identidades)
                        gravado = True
                    if gravado:
                        self._por_identidade.update(identidades)

    def _orientacao(
        self, dados: dict, orientador_id: int, identidades: Dict[str, int]
    ) -> None:
        orientacao_id = self._gravar_juntando(
            PASSO_ORIENTACOES,
            dados,
            TIPO_ORIENTACAO,
            (TIPO_ORIENTACAO,),
            identidades,
        )
        inicio = dados.get("start_date")
        self._ctx.iniciativas.adicionar_participante(
            orientacao_id, orientador_id, self._papeis["orientador"], inicio, None
        )
        for aluno in dados.get("student_names") or []:
            self._participante(orientacao_id, aluno, "orientando", inicio)
        self._ctx.relatorio.descartar(PASSO_ORIENTACOES, "tipo_e_instituicao")

    # ------------------------------------------------------------ comuns
    def _garantir_papeis(self, *nomes: str) -> None:
        for nome in nomes:
            self._papeis[nome] = self._ctx.organizacoes.garantir_papel(
                nome, "participacao"
            )

    def _gravar_juntando(
        self,
        passo: str,
        dados: dict,
        tipo: str,
        tipos_para_juntar: Tuple[str, ...],
        identidades: Dict[str, int],
    ) -> int:
        """Junta com a iniciativa de mesma identidade ou mesmo nome (sem
        sobrescrever: só preenche o que está vazio); senão cria."""
        titulo = texto(dados.get("title"))
        if not titulo:
            raise ValueError("iniciativa sem título")
        identidade = dados.get("identity_key")
        situacao = situacao_iniciativa(dados.get("status"), dados.get("end_date"))
        campos = {
            "situacao": situacao,
            "descricao": texto(dados.get("description")),
            "data_inicio": dados.get("start_date"),
            "data_fim": dados.get("end_date"),
        }

        existente = self._por_identidade.get(identidade) if identidade else None
        if existente is None:
            existente = self._por_nome(titulo, tipos_para_juntar)

        if existente is None:
            iniciativa_id = self._ctx.iniciativas.criar(
                titulo,
                tipo,
                self._ifes_id,
                situacao,
                campos["descricao"],
                campos["data_inicio"],
                campos["data_fim"],
            )
            self._ctx.relatorio.contar(passo, f"{tipo}_criadas")
        else:
            iniciativa_id = existente
            self._preencher_vazios(iniciativa_id, campos)
            self._ctx.relatorio.contar(passo, f"{tipo}_juntadas")

        if identidade:
            identidades[identidade] = iniciativa_id
        return iniciativa_id

    def _por_nome(self, nome: str, tipos: Tuple[str, ...]) -> Optional[int]:
        ids = [
            iniciativa.id
            for tipo in tipos
            for iniciativa in self._ctx.iniciativas.buscar_por_nome(nome, tipo)
        ]
        return min(ids) if ids else None

    def _preencher_vazios(self, iniciativa_id: int, campos: Dict[str, Any]) -> None:
        atual = self._ctx.iniciativas.buscar(iniciativa_id)
        novos = {
            campo: valor
            for campo, valor in campos.items()
            if valor not in (None, "")
            and getattr(atual, campo) in (None, "")
            and campo != "situacao"
        }
        if atual.situacao == "desconhecida" and campos["situacao"] != "desconhecida":
            novos["situacao"] = campos["situacao"]
        if novos:
            self._ctx.iniciativas.atualizar(iniciativa_id, novos)

    def _participante(
        self, iniciativa_id: int, nome: Any, papel: str, inicio: Any
    ) -> None:
        nome = texto(nome)
        if not nome:
            return
        pessoa = self._ctx.casamento_pessoas.match_or_create(nome, strict_match=True)
        if pessoa is None:
            return
        self._ctx.iniciativas.adicionar_participante(
            iniciativa_id, pessoa.id, self._papeis[papel], inicio, None
        )

    def _indice_coautores(self) -> Dict[str, int]:
        """Nome completo ou nome de citação normalizado → pessoa, só sem ambiguidade."""
        candidatos: Dict[str, Set[int]] = defaultdict(set)
        for pessoa in self._ctx.pessoas.listar():
            chave = normalize_text(pessoa.nome)
            if chave:
                candidatos[chave].add(pessoa.id)
        for pessoa_id, nomes in self._ctx.pessoas.listar_nomes_citacao():
            for nome in (nomes or "").split(";"):
                chave = normalize_text(nome)
                if chave:
                    candidatos[chave].add(pessoa_id)
        return {
            chave: next(iter(ids)) for chave, ids in candidatos.items() if len(ids) == 1
        }

    def _casar_coautores(self, autores: Any) -> List[int]:
        encontrados = []
        for nome in str(autores or "").split(";"):
            pessoa_id = self._coautores.get(normalize_text(nome))
            if pessoa_id is not None and pessoa_id not in encontrados:
                encontrados.append(pessoa_id)
        return encontrados
