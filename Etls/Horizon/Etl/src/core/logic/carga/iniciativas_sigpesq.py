"""Carga dos projetos e bolsistas do SigPesq no banco Horizon.

Segue as regras do ProjectLoader antigo para o SigPesq:

* só entram projetos com parecer aprovado (ou sem parecer);
* a iniciativa é casada pela identidade (código SigPesq) dentro da execução;
* coordenador, pesquisadores e estudantes viram participantes, com o início do projeto;
* o grupo do projeto é ligado como executor; grupo que não existe é criado no
  campus do projeto (ou na Reitoria) com os membros do projeto;
* palavras-chave viram áreas da iniciativa, do grupo e dos pesquisadores;
* o bolsista gera uma orientação filha do projeto (o pai é criado provisório se
  faltar), com orientador, orientando e bolsa; orientador e orientando também
  entram no projeto pai, cujas datas e situação são recalculadas no fim.

Decisões da migração aplicadas aqui: organização = campus de execução (senão
IFES), situação em português, sufixo "| Orientacao ..." mantido, demandante e
financiadora em organizacoes_iniciativa, área do projeto, bolsa sem financiador
pulada. O identificador da iniciativa só vale dentro da execução (recarga completa).

Diferença decidida em relação ao ProjectLoader: com código, só o código casa.
Linhas com o mesmo título e códigos diferentes viram iniciativas diferentes (o
código antigo as juntava pelo nome). O nome só é usado em linha sem código.
"""

from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

from src.core.logic.carga.contexto import ContextoCarga
from src.core.logic.carga.regras import situacao_iniciativa, situacao_pela_data, texto
from src.core.logic.initiative_identity import build_identity_key
from src.core.logic.strategies.sigpesq_advisorships import (
    SigPesqAdvisorshipMappingStrategy,
)
from src.core.logic.strategies.sigpesq_projects import SigPesqProjectMappingStrategy
from src.core.logic.tipo_organizacao import tipo_organizacao_por_nome

PASSO_PROJETOS = "projetos_sigpesq"
PASSO_BOLSISTAS = "bolsistas_sigpesq"
TIPO_PROJETO = "projeto_pesquisa"
TIPO_ORIENTACAO = "orientacao"
CAMPUS_PADRAO_GRUPO = "Reitoria"
SITUACOES_RECALCULAVEIS = {"desconhecida", "em_andamento", "concluida"}


def aprovado(linha: Dict[str, Any]) -> bool:
    """Mesmo filtro do ProjectLoader: parecer vazio ou contendo "aprovado"."""
    parecer = linha.get("ParecerDiretoria", "Aprovado")
    if isinstance(parecer, str) and parecer.strip():
        return "aprovado" in parecer.lower()
    return True


def nome_campus(valor: Any) -> Optional[str]:
    """Campus válido: como no código antigo, nomes com até 3 letras são ignorados."""
    campus = texto(valor)
    return campus if campus and len(campus) > 3 else None


def _pares(nomes: List[str], emails: Optional[List[Optional[str]]]) -> List[tuple]:
    emails = emails or [None] * len(nomes)
    return list(zip(nomes, emails))


class CarregadorIniciativasSigpesq:
    """Projetos e bolsistas. Use a mesma instância para os dois passos: os
    bolsistas encontram o projeto pai pela identidade gravada nos projetos."""

    def __init__(
        self,
        contexto: ContextoCarga,
        estrategia_projetos: Optional[SigPesqProjectMappingStrategy] = None,
        estrategia_bolsistas: Optional[SigPesqAdvisorshipMappingStrategy] = None,
    ):
        self._ctx = contexto
        self._estrategia_projetos = (
            estrategia_projetos or SigPesqProjectMappingStrategy()
        )
        self._estrategia_bolsistas = (
            estrategia_bolsistas or SigPesqAdvisorshipMappingStrategy()
        )
        self._por_identidade: Dict[str, int] = {}

    def projetos_por_codigo(self) -> Dict[str, int]:
        """Código SigPesq → id dos projetos (aprovados) carregados nesta execução.

        Substitui o índice que o enriquecimento PJ lia das tabelas de rastreamento.
        """
        prefixo = build_identity_key(["sigpesq_project"]) + "|"
        return {
            chave[len(prefixo) :]: iniciativa_id
            for chave, iniciativa_id in self._por_identidade.items()
            if chave.startswith(prefixo) and chave[len(prefixo) :].isdigit()
        }

    # ------------------------------------------------------------ projetos
    def carregar_projetos_arquivo(self, caminho: str) -> None:
        self.carregar_projetos(_ler_planilha(caminho))

    def carregar_projetos(self, linhas: Iterable[dict]) -> None:
        with self._ctx.passo(PASSO_PROJETOS):
            self._preparar()
            for numero, linha in enumerate(linhas, start=1):
                if not aprovado(linha):
                    self._ctx.relatorio.contar(PASSO_PROJETOS, "nao_aprovados")
                    continue
                dados = self._estrategia_projetos.map_row(linha)
                titulo = texto(dados.get("title"))
                if not titulo:
                    self._ctx.relatorio.pular(
                        PASSO_PROJETOS, "projeto sem título", f"linha {numero}"
                    )
                    continue

                identidades: Dict[str, int] = {}
                gravado = False
                with self._ctx.registro(PASSO_PROJETOS, f"projeto {titulo}"):
                    self._carregar_projeto(dados, titulo, identidades)
                    gravado = True
                if gravado:
                    self._por_identidade.update(identidades)

    def _carregar_projeto(
        self, dados: dict, titulo: str, identidades: Dict[str, int]
    ) -> None:
        identidade = dados.get("identity_key")
        campos = {
            "nome": titulo,
            "situacao": situacao_iniciativa(dados.get("status"), dados.get("end_date")),
            "descricao": texto(dados.get("description")),
            "data_inicio": dados.get("start_date"),
            "data_fim": dados.get("end_date"),
            "organizacao_id": self._organizacao(dados.get("campus_name")),
        }
        existente = self._existente(identidade, titulo, TIPO_PROJETO)
        projeto_id = self._gravar(PASSO_PROJETOS, TIPO_PROJETO, campos, existente)
        if identidade:
            identidades[identidade] = projeto_id

        inicio = dados.get("start_date")
        self._participante(
            projeto_id,
            dados.get("coordinator_name"),
            dados.get("coordinator_email"),
            "coordenador",
            inicio,
        )
        for nome, email in _pares(
            dados.get("researcher_names") or [], dados.get("researcher_emails")
        ):
            self._participante(projeto_id, nome, email, "pesquisador", inicio)
        for nome, email in _pares(
            dados.get("student_names") or [], dados.get("student_emails")
        ):
            self._participante(projeto_id, nome, email, "estudante", inicio)

        nome_grupo = texto(dados.get("research_group_name"))
        if nome_grupo:
            self._ligar_grupo(projeto_id, nome_grupo, dados)
        self._ligar_areas(projeto_id, dados, nome_grupo)

        metadados = dados.get("metadata") or {}
        self._ligar_organizacao_por_nome(
            projeto_id, metadados.get("external_partner"), "demandante"
        )
        if texto(dados.get("value")):
            self._ctx.relatorio.descartar(PASSO_PROJETOS, "valor_aprovado")
        if texto(metadados.get("external_research_group")):
            self._ctx.relatorio.descartar(PASSO_PROJETOS, "grupo_pesquisa_externo")

    def _ligar_grupo(self, projeto_id: int, nome_grupo: str, dados: dict) -> None:
        grupo_id = self._ctx.equipes.buscar_grupo_por_nome(nome_grupo)
        if grupo_id is None:
            campus = texto(dados.get("campus_name")) or CAMPUS_PADRAO_GRUPO
            if len(campus) <= 3:
                self._ctx.relatorio.pular(
                    PASSO_PROJETOS, "grupo do projeto sem campus válido", nome_grupo
                )
                return
            campus_id = self._ctx.organizacoes.garantir_unidade(campus, self._ifes_id)
            grupo_id, _ = self._ctx.equipes.garantir_grupo(
                nome_grupo,
                campus_id,
                descricao=f"Grupo de Pesquisa importado do SigPesq: {nome_grupo}",
            )
            self._copiar_membros_para_grupo(grupo_id, dados)
            self._ctx.relatorio.contar(PASSO_PROJETOS, "grupos_criados_pelo_projeto")

        self._ctx.iniciativas.ligar_equipe(projeto_id, grupo_id, "executor")

    def _copiar_membros_para_grupo(self, grupo_id: int, dados: dict) -> None:
        inicio = dados.get("start_date")
        pesquisadores = []
        if dados.get("coordinator_name"):
            pesquisadores.append(
                (dados.get("coordinator_name"), dados.get("coordinator_email"))
            )
        pesquisadores += _pares(
            dados.get("researcher_names") or [], dados.get("researcher_emails")
        )
        estudantes = _pares(
            dados.get("student_names") or [], dados.get("student_emails")
        )
        for membros, papel in (
            (pesquisadores, self._papeis["equipe:pesquisador"]),
            (estudantes, self._papeis["equipe:estudante"]),
        ):
            for nome, email in membros:
                pessoa = self._pessoa(nome, email)
                if pessoa is not None:
                    self._ctx.equipes.adicionar_membro(
                        grupo_id, pessoa, papel, inicio, None
                    )

    def _ligar_areas(
        self, projeto_id: int, dados: dict, nome_grupo: Optional[str]
    ) -> None:
        metadados = dados.get("metadata") or {}
        area_projeto = texto(metadados.get("knowledge_area"))
        if area_projeto:
            self._ctx.areas.ligar_area_iniciativa(
                projeto_id, self._ctx.areas.garantir_area(area_projeto)
            )

        palavras = texto(metadados.get("keywords"))
        if not palavras:
            return
        separador = ";" if ";" in palavras else ","
        area_ids = [
            self._ctx.areas.garantir_area(termo.strip())
            for termo in palavras.split(separador)
            if termo.strip()
        ]

        grupo_id = (
            self._ctx.equipes.buscar_grupo_por_nome(nome_grupo) if nome_grupo else None
        )
        pessoas = []
        for nome in [dados.get("coordinator_name")] + list(
            dados.get("researcher_names") or []
        ):
            pessoa = self._pessoa(nome, None) if nome else None
            if pessoa is not None:
                pessoas.append(pessoa)

        for area_id in area_ids:
            self._ctx.areas.ligar_area_iniciativa(projeto_id, area_id)
            if grupo_id is not None:
                self._ctx.areas.ligar_area_equipe(grupo_id, area_id)
            for pessoa in pessoas:
                self._ctx.areas.ligar_area_pessoa(pessoa, area_id)

    # ------------------------------------------------------------ bolsistas
    def carregar_bolsistas_arquivos(self, caminhos: Iterable[str]) -> None:
        linhas: List[dict] = []
        for caminho in caminhos:
            linhas.extend(_ler_planilha(caminho))
        self.carregar_bolsistas(linhas)

    def carregar_bolsistas(self, linhas: Iterable[dict]) -> None:
        with self._ctx.passo(PASSO_BOLSISTAS):
            self._preparar()
            for numero, linha in enumerate(linhas, start=1):
                if not aprovado(linha):
                    self._ctx.relatorio.contar(PASSO_BOLSISTAS, "nao_aprovados")
                    continue
                dados = self._estrategia_bolsistas.map_row(linha)
                titulo = texto(dados.get("title"))
                if not titulo:
                    self._ctx.relatorio.pular(
                        PASSO_BOLSISTAS,
                        "bolsista sem nome/e-mail ou plano sem título",
                        f"linha {numero}",
                    )
                    continue

                identidades: Dict[str, int] = {}
                gravado = False
                with self._ctx.registro(PASSO_BOLSISTAS, f"orientação {titulo}"):
                    self._carregar_orientacao(linha, dados, titulo, identidades)
                    gravado = True
                if gravado:
                    self._por_identidade.update(identidades)

            self._recalcular_projetos_pai()

    def _carregar_orientacao(
        self, linha: dict, dados: dict, titulo: str, identidades: Dict[str, int]
    ) -> None:
        pai_id = self._projeto_pai(dados, identidades)

        identidade = dados.get("identity_key")
        existente = self._existente(identidade, titulo, TIPO_ORIENTACAO)
        nome = self._nome_orientacao(titulo, dados, existente)

        campos = {
            "nome": nome,
            "situacao": situacao_iniciativa(dados.get("status"), dados.get("end_date")),
            "descricao": texto(dados.get("description")),
            "data_inicio": dados.get("start_date"),
            "data_fim": dados.get("end_date"),
            "organizacao_id": self._organizacao(dados.get("campus_name")),
        }
        orientacao_id = self._gravar(
            PASSO_BOLSISTAS, TIPO_ORIENTACAO, campos, existente
        )
        if identidade:
            identidades[identidade] = orientacao_id
        if pai_id is not None:
            self._ctx.iniciativas.definir_pai(orientacao_id, pai_id)

        inicio = dados.get("start_date")
        aluno = self._primeiro(dados.get("student_names"))
        email_aluno = self._primeiro(dados.get("student_emails"))
        orientando = self._participante(
            orientacao_id, aluno, email_aluno, "orientando", inicio
        )
        self._participante(
            orientacao_id,
            dados.get("coordinator_name"),
            dados.get("coordinator_email"),
            "orientador",
            inicio,
        )
        self._bolsa(linha, dados, orientacao_id, orientando, nome)

        if pai_id is not None:
            self._participante(
                pai_id,
                dados.get("coordinator_name"),
                dados.get("coordinator_email"),
                "pesquisador",
                inicio,
            )
            self._participante(pai_id, aluno, email_aluno, "estudante", inicio)

        if dados.get("cancelled"):
            self._ctx.relatorio.descartar(PASSO_BOLSISTAS, "dados_cancelamento")

    def _projeto_pai(self, dados: dict, identidades: Dict[str, int]) -> Optional[int]:
        titulo_pai = texto(dados.get("parent_title"))
        if not titulo_pai:
            return None
        identidade_pai = dados.get("parent_identity_key")
        pai_id = self._existente(identidade_pai, titulo_pai, TIPO_PROJETO)
        if pai_id is None:
            pai_id = self._ctx.iniciativas.criar(
                titulo_pai, TIPO_PROJETO, self._ifes_id, "desconhecida"
            )
            self._ctx.relatorio.contar(PASSO_BOLSISTAS, "projetos_pai_provisorios")
        if identidade_pai:
            identidades[identidade_pai] = pai_id
        return pai_id

    def _nome_orientacao(
        self, titulo: str, dados: dict, atual_id: Optional[int]
    ) -> str:
        """Como no ETL antigo: se outra iniciativa já usa o título, acrescenta
        aluno, ano e id do SigPesq."""
        em_uso = any(
            iniciativa.id != atual_id
            for iniciativa in self._ctx.iniciativas.buscar_por_nome(titulo)
        )
        if not em_uso:
            return titulo

        partes = []
        aluno = next(
            (
                nome
                for nome in dados.get("student_names") or []
                if isinstance(nome, str) and nome.strip()
            ),
            None,
        )
        if aluno:
            partes.append(aluno)
        inicio = dados.get("start_date")
        if isinstance(inicio, (date, datetime)):
            partes.append(str(inicio.year))
        sigpesq_id = (dados.get("metadata") or {}).get("sigpesq_id")
        if sigpesq_id:
            partes.append(f"sigpesq {sigpesq_id}")
        if not partes and dados.get("identity_key"):
            partes.append(str(dados["identity_key"])[:24])
        return f"{titulo} | Orientacao {' | '.join(partes)}".strip()

    def _bolsa(
        self,
        linha: dict,
        dados: dict,
        orientacao_id: int,
        orientando: Optional[int],
        nome_orientacao: str,
    ) -> None:
        financiadora = texto(linha.get("AgFinanciadora", linha.get("agFinanciadora")))
        financiador_id = None
        if financiadora:
            financiador_id = self._ctx.organizacoes.garantir_organizacao(
                financiadora, "fomento"
            )
            self._ctx.iniciativas.ligar_organizacao(
                orientacao_id, financiador_id, "financiadora"
            )

        bolsa = dados.get("fellowship_data") or {}
        nome_bolsa = texto(bolsa.get("name"))
        if not nome_bolsa:
            return
        if financiador_id is None:
            self._ctx.relatorio.pular(
                PASSO_BOLSISTAS,
                "bolsa sem financiador",
                f"{nome_bolsa} em {nome_orientacao}",
            )
            return
        bolsa_id = self._ctx.iniciativas.garantir_bolsa(
            nome_bolsa, financiador_id, bolsa.get("value") or 0.0
        )
        if orientando is not None:
            self._ctx.iniciativas.definir_bolsa_participante(orientando, bolsa_id)

    def _recalcular_projetos_pai(self) -> None:
        """Datas do pai só se ampliam; a situação segue a data de fim resultante."""
        for pai_id, (
            inicio,
            fim,
        ) in self._ctx.iniciativas.periodos_dos_filhos().items():
            pai = self._ctx.iniciativas.buscar(pai_id)
            if pai is None:
                continue
            campos: Dict[str, Any] = {}
            if inicio and (pai.data_inicio is None or inicio < pai.data_inicio):
                campos["data_inicio"] = inicio
            if fim and (pai.data_fim is None or fim > pai.data_fim):
                campos["data_fim"] = fim
            fim_resultante = campos.get("data_fim", pai.data_fim)
            if fim_resultante and pai.situacao in SITUACOES_RECALCULAVEIS:
                situacao = situacao_pela_data(fim_resultante)
                if situacao != pai.situacao:
                    campos["situacao"] = situacao
            if campos:
                self._ctx.iniciativas.atualizar(pai_id, campos)
                self._ctx.relatorio.contar(PASSO_BOLSISTAS, "projetos_pai_recalculados")

    # ------------------------------------------------------------ comuns
    def _preparar(self) -> None:
        organizacoes = self._ctx.organizacoes
        self._ifes_id = organizacoes.ifes_id()
        self._papeis = {
            f"{escopo}:{nome}": organizacoes.garantir_papel(nome, escopo)
            for escopo, nome in (
                ("participacao", "coordenador"),
                ("participacao", "pesquisador"),
                ("participacao", "estudante"),
                ("participacao", "orientador"),
                ("participacao", "orientando"),
                ("equipe", "pesquisador"),
                ("equipe", "estudante"),
            )
        }

    def _organizacao(self, campus: Any) -> int:
        nome = nome_campus(campus)
        if nome is None:
            return self._ifes_id
        return self._ctx.organizacoes.garantir_unidade(nome, self._ifes_id)

    def _existente(
        self, identidade: Optional[str], nome: str, tipo: str
    ) -> Optional[int]:
        """Com código, só o código casa; sem código, o nome exato do mesmo tipo."""
        if identidade:
            return self._por_identidade.get(identidade)
        candidatos = self._ctx.iniciativas.buscar_por_nome(nome, tipo)
        return candidatos[0].id if candidatos else None

    def _gravar(
        self,
        passo: str,
        tipo: str,
        campos: Dict[str, Any],
        existente: Optional[int],
    ) -> int:
        if existente is None:
            self._ctx.relatorio.contar(passo, f"{tipo}_criadas")
            return self._ctx.iniciativas.criar(
                campos["nome"],
                tipo,
                campos["organizacao_id"],
                campos["situacao"],
                campos["descricao"],
                campos["data_inicio"],
                campos["data_fim"],
            )
        self._ctx.iniciativas.atualizar(existente, campos)
        self._ctx.relatorio.contar(passo, f"{tipo}_atualizadas")
        return existente

    def _pessoa(self, nome: Any, email: Any) -> Optional[int]:
        nome, email = texto(nome), texto(email)
        if not nome and not email:
            return None
        pessoa = self._ctx.casamento_pessoas.match_or_create(
            nome, email=email, strict_match=True
        )
        return pessoa.id if pessoa is not None else None

    def _participante(
        self,
        iniciativa_id: int,
        nome: Any,
        email: Any,
        papel: str,
        inicio: Optional[datetime],
    ) -> Optional[int]:
        pessoa = self._pessoa(nome, email)
        if pessoa is None:
            return None
        participante_id, _ = self._ctx.iniciativas.adicionar_participante(
            iniciativa_id,
            pessoa,
            self._papeis[f"participacao:{papel}"],
            inicio,
            None,
        )
        return participante_id

    def _ligar_organizacao_por_nome(
        self, iniciativa_id: int, nome: Any, papel: str
    ) -> None:
        nome = texto(nome)
        if not nome:
            return
        organizacao_id = self._ctx.organizacoes.garantir_organizacao(
            nome, tipo_organizacao_por_nome(nome)
        )
        self._ctx.iniciativas.ligar_organizacao(iniciativa_id, organizacao_id, papel)

    @staticmethod
    def _primeiro(valores: Optional[List[Any]]) -> Any:
        return valores[0] if valores else None


def _ler_planilha(caminho: str) -> List[dict]:
    """Como o ProjectLoader: células vazias viram texto vazio."""
    return pd.read_excel(caminho).fillna("").to_dict("records")
