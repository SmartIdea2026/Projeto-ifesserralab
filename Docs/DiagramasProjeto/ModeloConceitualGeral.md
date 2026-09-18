# Modelo Conceitual Integrado de Dados: Diretoria, SRC e Horizon (IFES Campus Serra)

## 1. Visão Geral e Contexto da Integração

O ecossistema de dados do IFES Campus Serra é composto por múltiplos sistemas independentes que cobrem diferentes verticais acadêmicas e administrativas:
- **Diretoria & SRC (Extensão e Ensino)**: Extraído do *Sistema de Registro e Emissão de Certificados (SRC)* e publicado como API estática / relatórios da Diretoria. Concentra ações de extensão/ensino, atividades curriculares, histórico de extensionistas (docentes, discentes e convidados), público-alvo atendido e indicadores de impacto.
- **Horizon (Pesquisa e Pós-Graduação)**: Plataforma integrada de pesquisa e governança institucional, consolidando dados do *SIGPesq*, *Plataforma Lattes/CNPq* e publicações acadêmicas em arquivos colunares Parquet e agregados JSON.

A integração conceitual aqui apresentada unifica as bases de **Diretoria**, **SRC** e **Horizon**, atendendo rigorosamente às seguintes diretrizes:
1. **Unificação sem duplicidade**: Tabelas e atributos idênticos ou equivalentes entre **Diretoria** e **SRC** foram fundidos em uma única entidade concentradora com a totalidade dos atributos de ambas as fontes.
2. **Fidelidade aos dados reais**: Não foram inventadas tabelas artificiais, nem chaves primárias (PK) ou estrangeiras (FK) que não existam ou não façam sentido nos dados brutos. Tabelas sem vínculo referencial direto com outras foram mantidas soltas (*standalone*).
3. **Isolamento de escopo**: Bases de Egressos, Editais e GeDoc foram expressamente excluídas do escopo.
4. **Sem fontes externas**: Utilizou-se estritamente os arquivos e dicionários locais presentes na pasta do projeto.

---

## 2. Análise de Entidades e Atributos em Comum

### 2.1. Entidades em Comum e Cruzamentos Semânticos

| Entidade Conceitual | Em Diretoria / SRC | Em Horizon | Grau de Correspondência | Observações sobre Chaves e Cruzamento |
| :--- | :--- | :--- | :--- | :--- |
| **Pessoa / Agente Acadêmico** | `EXTENSIONISTA` (`api/extensionistas/*.json`) | `PESSOA` (`pessoas_canonical` / `researchers_canonical`) | **Conceitual Alto** (Mesmo indivíduo físico) | Em Horizon a PK é `id` (Int64). Em SRC/Diretoria a PK é `slug` (String). O cruzamento real ocorre por chave natural (`nome` / `name`), catalogado pelo Horizon via `entity_matches_canonical` (`canonical_name`). |
| **Iniciativa / Projeto** | `ACAO_EXTENSAO` (`api/acoes/*.json`) | `INICIATIVA_PESQUISA` (`initiatives_canonical`) | **Conceitual Médio** (Tipos distintos de projeto) | Ambas representam projetos institucionais com equipe, coordenador, resumo e campus. Porém, `ACAO_EXTENSAO` vem do SIPAC/SRC (Extensão/Ensino) e `INICIATIVA_PESQUISA` do SIGPesq (Pesquisa). Foram mantidas como entidades distintas especializadas para preservar a integridade dos atributos específicos. |
| **Campus** | `Campus: "Serra"` (atributo textual) | `CAMPUS` (`campuses_canonical`: `id: 6`) | **Conceitual Alto** | Ambas se referem às unidades do IFES. No Horizon é uma tabela canônica estruturada; no SRC/Diretoria é um atributo denormalizado fixo no Campus Serra. |
| **Área do Conhecimento** | `Grande área conhecimento`, `Área temática` | `AREA_CONHECIMENTO` (`knowledge_areas_canonical`) | **Conceitual Alto** | Ambas utilizam a taxonomia oficial de áreas do CNPq/CAPES (ex.: Educação, Ciências Sociais Aplicadas, Ciência da Computação). |
| **Fomento / Financiamento** | `Fomento` (PAEX-IFES, PRONATEC, Mulheres Mil, Sem Vínculo) | `PROGRAMA_BOLSA` (`fellowships_canonical`: PIVIC, PIBIC, etc.) | **Conceitual Médio** | Horizon foca em bolsas de pesquisa acadêmica; SRC/Diretoria foca em programas de fomento institucional à extensão. |

---

## 3. Modelo Entidade-Relacionamento Conceitual (Mermaid)

```mermaid
erDiagram
    ORGANIZACAO ||--o{ CAMPUS : "possui"
    CAMPUS ||--o{ CAMPUS : "subordina (hierarquia)"
    CAMPUS ||--o{ PESSOA : "aloca"
    CAMPUS ||--o{ INICIATIVA_PESQUISA : "sedia"
    CAMPUS ||--o{ GRUPO_PESQUISA : "sedia"
    CAMPUS ||--o{ ARTIGO : "vincula"

    ORGANIZACAO ||--o{ INICIATIVA_PESQUISA : "mantem"
    ORGANIZACAO ||--o{ GRUPO_PESQUISA : "institui"

    TIPO_INICIATIVA ||--o{ INICIATIVA_PESQUISA : "classifica"
    INICIATIVA_PESQUISA ||--o{ INICIATIVA_PESQUISA : "vincula_parent (autorrelacionamento)"
    
    INICIATIVA_PESQUISA ||--o{ MEMBRO_EQUIPE_INICIATIVA : "possui_equipe"
    PESSOA ||--o{ MEMBRO_EQUIPE_INICIATIVA : "integra"

    INICIATIVA_PESQUISA ||--o{ INICIATIVA_AREA_CONHECIMENTO : "enquadra"
    AREA_CONHECIMENTO ||--o{ INICIATIVA_AREA_CONHECIMENTO : "abrange"

    GRUPO_PESQUISA ||--o{ MEMBRO_GRUPO_PESQUISA : "compoe"
    PESSOA ||--o{ MEMBRO_GRUPO_PESQUISA : "participa"

    GRUPO_PESQUISA ||--o{ GRUPO_AREA_CONHECIMENTO : "atua_em"
    AREA_CONHECIMENTO ||--o{ GRUPO_AREA_CONHECIMENTO : "delimita"

    PESSOA ||--o{ ORIENTACAO : "orientando (person_id)"
    PESSOA ||--o{ ORIENTACAO : "supervisor (supervisor_id)"
    PROGRAMA_BOLSA ||--o{ ORIENTACAO : "financia"
    CAMPUS ||--o{ ORIENTACAO : "localiza"

    GOVERNANCA_EXECUCAO_INGESTAO ||--o{ GOVERNANCA_LOG_ALTERACAO : "registra"

    ACAO_EXTENSAO ||--o{ ATIVIDADE_EXTENSAO : "desdobra_em"
    ACAO_EXTENSAO ||--o{ EQUIPE_EXECUCAO_EXTENSAO : "aloca_equipe"
    ATIVIDADE_EXTENSAO ||--o{ EQUIPE_EXECUCAO_EXTENSAO : "executa_com"
    
    ACAO_EXTENSAO ||--o{ PENDENCIA_RELATORIO_EXTENSAO : "acompanha_pendencia"
    EXTENSIONISTA ||--o{ PENDENCIA_RELATORIO_EXTENSAO : "coordena_pendencia"

    ACAO_EXTENSAO ||--o{ ACAO_SEM_PARTICIPACAO : "sinaliza_vazio"

    EXTENSIONISTA ||--o{ COLABORACAO_EXTENSIONISTA : "colabora_origem"
    EXTENSIONISTA ||--o{ COLABORACAO_EXTENSIONISTA : "colabora_parceiro"

    ORGANIZACAO {
        int id PK
        string name
        string short_name
        string description
    }

    CAMPUS {
        int id PK
        string name
        string short_name
        int organization_id FK
        int parent_id FK
        string description
    }

    TIPO_INICIATIVA {
        int id PK
        string name
        string description
    }

    AREA_CONHECIMENTO {
        int id PK
        string name
    }

    PROGRAMA_BOLSA {
        int id PK
        string name
        float value
        string description
    }

    PESSOA {
        int id PK
        string name
        string identification_id
        string classification
        string classification_confidence
        string classification_note
        boolean was_student
        boolean was_staff
        string cnpq_url
        string resume
        string citation_names
        int campus_id FK
    }

    INICIATIVA_PESQUISA {
        int id PK
        string name
        string status
        string description
        datetime start_date
        datetime end_date
        int initiative_type_id FK
        int organization_id FK
        int parent_id FK
        int campus_id FK
        string sigpesq_code
        string match_strategy
        boolean needs_review
        string linha_pesquisa
        string area_conhecimento_texto
    }

    MEMBRO_EQUIPE_INICIATIVA {
        int initiative_id FK
        int person_id FK
        string person_name
        string roles
        datetime start_date
        datetime end_date
    }

    INICIATIVA_AREA_CONHECIMENTO {
        int initiative_id FK
        int knowledge_area_id FK
    }

    GRUPO_PESQUISA {
        int id PK
        string name
        string short_name
        string description
        string cnpq_url
        string site
        int organization_id FK
        int campus_id FK
    }

    MEMBRO_GRUPO_PESQUISA {
        int group_id FK
        int person_id FK
        string role
        date start_date
        date end_date
    }

    GRUPO_AREA_CONHECIMENTO {
        int group_id FK
        int knowledge_area_id FK
    }

    ORIENTACAO {
        int id PK
        string name
        string status
        string description
        datetime start_date
        datetime end_date
        int person_id FK
        int supervisor_id FK
        int fellowship_id FK
        int campus_id FK
    }

    ARTIGO {
        int id PK
        string title
        string doi
        int year
        string type
        string journal_conference
        string volume
        string pages
        int campus_id FK
    }

    GOVERNANCA_EXECUCAO_INGESTAO {
        int id PK
        string pipeline_name
        string run_status
        string source_system
        string input_snapshot_hash
        datetime started_at
        datetime finished_at
    }

    GOVERNANCA_MATCH_ENTIDADE {
        int id PK
        int source_record_id
        string canonical_entity_type
        int canonical_entity_id
        string match_strategy
        string match_confidence
        datetime matched_at
        int campus_id FK
    }

    GOVERNANCA_LOG_ALTERACAO {
        int id PK
        int ingestion_run_id FK
        int source_record_id
        string canonical_entity_type
        int canonical_entity_id
        string operation
        string changed_fields_json
        string reason
        datetime changed_at
    }

    GOVERNANCA_ASSERCAO_ATRIBUTO {
        int id PK
        int source_record_id
        string canonical_entity_type
        int canonical_entity_id
        string attribute_name
        string value_json
        string value_hash
        boolean is_selected
        string selection_reason
        datetime asserted_at
    }

    ACAO_EXTENSAO {
        string acao_id PK
        string processo
        string titulo
        string tipo
        string natureza
        string coordenador
        string fomento
        string acao_vinculante
        string grande_area
        string grande_area_inferida
        string area_tematica
        string area_tematica_inferida
        string nicho_tematico
        string status_iniciativa
        string relatorio_aprovado
        string data_ultimo_relatorio
        string data_cadastro
        string ano
        int ano_ultima_atividade
        string resumo
        string campus
        int total_participacoes
        int publico_alvo_total
        string url
    }

    ATIVIDADE_EXTENSAO {
        string atividade_id PK
        string acao_id FK
        string numero
        string nome_atividade
        string acao_titulo
        string processo
        string coordenador_acao
        int publico_total
        int publico_aprovados
        int publico_certificados
        string publico_situacao
    }

    EXTENSIONISTA {
        string slug PK
        string nome
        string resumo_ia
        string anos
        string funcoes
        int imp_coord
        int imp_eq
        int impacto
        string url
    }

    EQUIPE_EXECUCAO_EXTENSAO {
        string acao_id FK
        string atividade_id FK
        string nome_membro
        string funcao
        string vinculo
    }

    COLABORACAO_EXTENSIONISTA {
        string extensionista_origem_slug FK
        string colaborador_slug FK
        string colaborador_nome
        int acoes_comuns
    }

    PENDENCIA_RELATORIO_EXTENSAO {
        string acao_id FK
        string titulo
        string tipo
        string coordenador
        string coordenador_slug FK
        string ano
        string inicio
        string termino
        string ultimo_relatorio
        boolean pendente
        int publico
        int equipe
    }

    ACAO_SEM_PARTICIPACAO {
        string acao_id FK
        string titulo
        string tipo
        string coordenador
        string ano
    }

    TEMA_NICHO_EXTENSAO {
        string tema PK
        string resumo
        int acoes_count
        int publico_total
        int pessoas_total
    }

    PAINEL_INDICADORES_EXTENSAO {
        int n_acoes
        int n_acoes_ativas
        int total_atividades
        int total_publico
        int total_equipe
        float taxa_certificacao
        int alunos_unicos
        int equipe_unica
        int total_formados
        int formados_em_extensao
        int horas_aluno
    }
```

---

## 4. Catálogo Detalhado de Tabelas Criadas e Suas Fontes

### 4.1. Tabelas Integradas de Extensão e Ensino (Diretoria + SRC Unificadas)

#### 1. `ACAO_EXTENSAO`
- **Fontes**: 
  - `diretoria/api/acoes/<acao_id>.json` (201 arquivos)
  - `SRC/api/acoes/<acao_id>.json` (201 arquivos)
  - `diretoria/Dicionario - Diretoria.xlsx` (abas `Diretoria_acoes.json`, `Diretoria_index.json`)
  - `SRC/SRC.xlsx` (abas `SRC_AcoesLista.json`, `SRC_BuscaIndice.json`, `SRC_Investimento.json`)
  - `SRC/api/busca.json` e `SRC/api/investimento.json` (iniciativas)
- **Justificativa de Unificação**: Os arquivos de ações em `diretoria` e `SRC` são rigorosamente os mesmos (hash idêntico). `SRC` complementa com nichos analíticos (`nicho`), status temporal (`status`: ativa, dormente, intermediária) e ano da última atividade. Ambas foram fundidas em uma única entidade concentradora.
- **Atributos**:
  - `acao_id` (String, PK): Identificador numérico único da ação no SRC.
  - `processo` (String): Processo administrativo (SIPAC), ex.: `23158.000916/2013-02`.
  - `titulo` (String): Título oficial completo da ação.
  - `tipo` (String): Modalidade (Projeto, Curso, Evento, Programa).
  - `natureza` (String): Natureza acadêmica (Extensão, Ensino).
  - `coordenador` (String): Nome do coordenador responsável.
  - `fomento` (String): Fonte de recurso (PAEX-IFES, PRONATEC, Mulheres Mil, SEM VÍNCULO).
  - `acao_vinculante` (String): Processo ou ação-mãe vinculadora.
  - `grande_area` / `grande_area_inferida` (String): Grande área de conhecimento segundo o CNPq.
  - `area_tematica` / `area_tematica_inferida` (String): Área temática oficial da extensão.
  - `nicho_tematico` (String): Cluster temático derivado em `SRC/api/investimento.json`.
  - `status_iniciativa` (String): Status operacional (ativa, dormente, intermediária).
  - `relatorio_aprovado` (String): Situação de aprovação do relatório final (Sim / Não).
  - `data_ultimo_relatorio` (String / Data): Data de entrega do último relatório.
  - `data_cadastro` (String / Data): Data de cadastro da ação no sistema.
  - `ano` (String): Ano de referência/início da ação.
  - `ano_ultima_atividade` (Int): Ano da última atividade executada (de SRC).
  - `resumo` (String): Resumo descritivo da ação.
  - `campus` (String): Campus IFES executor (Serra).
  - `total_participacoes` (Int): Total de atendimentos/participações registradas.
  - `publico_alvo_total` (Int): Público-alvo total contabilizado.
  - `url` (String): Endpoint relativo da documentação.

---

#### 2. `ATIVIDADE_EXTENSAO`
- **Fontes**:
  - `diretoria/api/atividades/<atividade_id>.json` (525 arquivos)
  - `SRC/api/atividades/<atividade_id>.json` (525 arquivos)
  - `diretoria/Dicionario - Diretoria.xlsx` (aba `Diretoria_atividades.json`)
- **Justificativa de Unificação**: Conteúdo 100% idêntico entre os diretórios de Diretoria e SRC.
- **Atributos**:
  - `atividade_id` (String, PK): Identificador numérico da atividade no SRC.
  - `acao_id` (String, FK -> `ACAO_EXTENSAO.acao_id`): Identificador da ação à qual a atividade pertence.
  - `numero` (String): Número identificador da atividade dentro da ação (ex.: "003").
  - `nome_atividade` (String): Título descritivo da atividade.
  - `acao_titulo` (String): Título da ação-mãe (desnormalizado na fonte).
  - `processo` (String): Processo da ação-mãe (desnormalizado na fonte).
  - `coordenador_acao` (String): Nome do coordenador da ação-mãe.
  - `publico_total` (Int): Total de participantes inscritos.
  - `publico_aprovados` (Int): Participantes com status APROVADO.
  - `publico_certificados` (Int): Participantes com certificado emitido.
  - `publico_situacao` (String / JSON): Distribuição numérica por situação de matrícula.

---

#### 3. `EXTENSIONISTA`
- **Fontes**:
  - `diretoria/api/extensionistas/<slug>.json` (757 pessoas + `todos.json`)
  - `SRC/api/extensionistas/<slug>.json` (757 pessoas + `todos.json`)
  - `diretoria/Dicionario - Diretoria.xlsx` (aba `Diretoria_extensionistas.json`)
  - `SRC/SRC.xlsx` (abas `SRC_ExtensionistasCompleto.json`, `SRC_ExtensionistasLista.json`)
- **Justificativa de Unificação**: Ambas as bases documentam as mesmas 757 pessoas. SRC enriquece o arquivo de cada extensionista com indicadores quantitativos de impacto acumulado (`imp_coord`, `imp_eq`, `impacto`).
- **Atributos**:
  - `slug` (String, PK): Identificador amigável e único para URL (ex.: `pedro-abraao-lino-da-silva`).
  - `nome` (String): Nome completo do extensionista.
  - `resumo_ia` (String): Biografia profissional e histórico de atuação gerado por IA.
  - `anos` (String / Array): Anos em que houve atividade registrada.
  - `funcoes` (String / Array): Funções exercidas ao longo do histórico (Instrutor, Coordenador, etc.).
  - `imp_coord` (Int): Impacto de público gerado como coordenador.
  - `imp_eq` (Int): Impacto de público gerado como integrante de equipe.
  - `impacto` (Int): Impacto total consolidado (`imp_coord` + `imp_eq`).
  - `url` (String): Caminho do arquivo JSON do extensionista.

---

#### 4. `EQUIPE_EXECUCAO_EXTENSAO`
- **Fontes**:
  - Array `equipe_execucao` em `diretoria/api/acoes/*.json` e `SRC/api/acoes/*.json`
  - Array `equipe_execucao` em `diretoria/api/atividades/*.json` e `SRC/api/atividades/*.json`
- **Papel**: Representa o vínculo associativo N:M entre membros da equipe e as Ações/Atividades de extensão.
- **Atributos**:
  - `acao_id` (String, FK -> `ACAO_EXTENSAO.acao_id`): Identificador da ação.
  - `atividade_id` (String, FK -> `ATIVIDADE_EXTENSAO.atividade_id`, opcional): Identificador da atividade específica, quando aplicável.
  - `nome_membro` (String): Nome completo da pessoa integrante.
  - `funcao` (String): Papel exercido (ex.: COORDENADOR(A) DE ÁREA, INSTRUTOR(A), ALUNO(A) VOLUNTARIO).
  - `vinculo` (String): Vínculo institucional (Servidor, Aluno, Convidado).

---

#### 5. `COLABORACAO_EXTENSIONISTA`
- **Fontes**:
  - Array `colaboradores` dentro de `diretoria/api/extensionistas/*.json` e `SRC/api/extensionistas/*.json`
- **Papel**: Representa a rede de coautoria/trabalho conjunto entre pares de extensionistas.
- **Atributos**:
  - `extensionista_origem_slug` (String, FK -> `EXTENSIONISTA.slug`): Extensionista de referência.
  - `colaborador_slug` (String, FK -> `EXTENSIONISTA.slug`): Colega parceiro de extensão.
  - `colaborador_nome` (String): Nome completo do parceiro.
  - `acoes_comuns` (Int): Quantidade de ações executadas em conjunto.

---

#### 6. `PENDENCIA_RELATORIO_EXTENSAO`
- **Fontes**:
  - `diretoria/api/pendencias-relatorio.json`
  - `SRC/api/pendencias-relatorio.json`
  - `diretoria/Dicionario - Diretoria.xlsx` (aba `Diretoria_pendenciasRelatorio.j`)
  - `SRC/SRC.xlsx` (aba `SRC_PendenciasRelatorio.json`)
- **Justificativa de Unificação**: Ambas controlam a aprovação de relatórios finais. A versão SRC contém colunas mais detalhadas (`coordenador_slug`, `inicio`, `termino`, `ultimo`, `pendente`, `pub`, `eq`), que foram integradas.
- **Atributos**:
  - `acao_id` (String, FK -> `ACAO_EXTENSAO.acao_id`): Ação auditada.
  - `titulo` (String): Título da ação.
  - `tipo` (String): Tipo da ação.
  - `coordenador` (String): Nome do coordenador responsável.
  - `coordenador_slug` (String, FK -> `EXTENSIONISTA.slug`, opcional): Slug do coordenador no SRC.
  - `ano` (String): Ano da ação.
  - `inicio` (String): Data de início registrada.
  - `termino` (String): Data de término registrada.
  - `ultimo_relatorio` (String): Data do último envio ou "nunca enviado".
  - `pendente` (Boolean): Flag binária de pendência de relatório ativa.
  - `publico` (Int): Público computado.
  - `equipe` (Int): Membros de equipe computados.

---

#### 7. `ACAO_SEM_PARTICIPACAO`
- **Fontes**:
  - `diretoria/api/sem-participacao.json`
  - `SRC/api/sem-participacao.json`
  - `diretoria/Dicionario - Diretoria.xlsx` (aba `Diretoria_semParticicapao.json`)
  - `SRC/SRC.xlsx` (aba `SRC_AcoesSemParticipacoes.json`)
- **Papel**: Subconjunto de ações homologadas no sistema institucional, porém sem registro efetivo de público-alvo ou de equipe executora.
- **Atributos**:
  - `acao_id` (String, FK -> `ACAO_EXTENSAO.acao_id`): Identificador da ação.
  - `titulo` (String): Título da ação.
  - `tipo` (String): Tipo da ação.
  - `coordenador` (String): Coordenador da ação.
  - `ano` (String): Ano de vigência.

---

#### 8. `TEMA_NICHO_EXTENSAO` (Tabela de Domínio / Agrupamento)
- **Fontes**:
  - `SRC/api/temas.json`
  - `SRC/api/investimento.json`
  - `SRC/SRC.xlsx` (aba `SRC_TemasClusters.json`)
- **Papel**: Clusters estratégicos de atuação da extensão (ex.: "Robótica e cultura maker", "Mulheres e inclusão").
- **Atributos**:
  - `tema` (String, PK): Nome oficial do eixo/nicho temático.
  - `resumo` (String): Escopo das ações abrangidas no nicho.
  - `acoes_count` (Int): Total de ações vinculadas.
  - `publico_total` (Int): Total de público alcançado pelo nicho.
  - `pessoas_total` (Int): Pessoas físicas únicas no nicho.

---

#### 9. `PAINEL_INDICADORES_EXTENSAO` (Tabela Solta / Agregada)
- **Fontes**:
  - `diretoria/api/painel.json`
  - `SRC/api/painel.json`
  - Abas de dicionário `Diretoria_painel.json` e `SRC_PainelAgregado.json`
- **Papel**: Tabela analítica desnormalizada (sem chave estrangeira relacional direta) reunindo os principais KPIs institucionais da extensão (visão geral, funil de certificação, distribuição por público e rede Forproex).
- **Atributos**: `n_acoes`, `n_acoes_ativas`, `total_atividades`, `total_publico`, `total_equipe`, `taxa_certificacao`, `alunos_unicos`, `equipe_unica`, `total_formados`, `formados_em_extensao`, `horas_aluno`.

---

### 4.2. Tabelas Canônicas de Pesquisa e Institucionais (Horizon)

#### 10. `ORGANIZACAO`
- **Fonte**: `horizon/organizations_canonical.parquet` e aba `organizations_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador da organização institucional.
  - `name` (String): Nome completo (ex.: "Instituto Federal do Espirito Santo").
  - `short_name` (String): Sigla (ex.: "IFES").
  - `description` (String): Descrição institucional.

---

#### 11. `CAMPUS`
- **Fonte**: `horizon/campuses_canonical.parquet` e aba `campuses_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador único do campus (ex.: 6 para Serra).
  - `name` (String): Nome do campus (ex.: "Serra", "Vitória", "Vila Velha").
  - `short_name` (String): Nome abreviado.
  - `organization_id` (Int, FK -> `ORGANIZACAO.id`): Organização mantenedora.
  - `parent_id` (Int, FK -> `CAMPUS.id`, autorrelacionamento): Hierarquia entre campi.
  - `description` (String): Detalhes do campus.

---

#### 12. `TIPO_INICIATIVA`
- **Fonte**: `horizon/initiative_types_canonical.parquet` e aba `initiative_types_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador do tipo de iniciativa.
  - `name` (String): Descritor do tipo (ex.: "Research Project").
  - `description` (String): Descrição detalhada do enquadramento.

---

#### 13. `AREA_CONHECIMENTO`
- **Fonte**: `horizon/knowledge_areas_canonical.parquet` e aba `knowledge_areas_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador da área na árvore CNPq/CAPES.
  - `name` (String): Nome da área (ex.: "Educação", "Ciência da Computação").

---

#### 14. `PROGRAMA_BOLSA`
- **Fonte**: `horizon/fellowships_canonical.parquet` e aba `fellowships_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador do programa de bolsa acadêmica.
  - `name` (String): Sigla do programa (PIVIC, PIBIC, PIBITI, etc.).
  - `value` (Float): Valor mensal estipulado da bolsa (em R$).
  - `description` (String): Descrição do edital/programa.

---

#### 15. `PESSOA`
- **Fontes**: 
  - `horizon/researchers_canonical.parquet` (base mãe completa com 10.089 registros)
  - Subconjuntos filtrados: `researchers_only_canonical.parquet`, `students_canonical.parquet`, `outside_ifes_canonical.parquet`, `null_researchers_canonical.parquet`
  - Aba `pessoas_canonical` em `dicionarioHorizon.xlsx`
- **Atributos**:
  - `id` (Int64, PK): Identificador único da pessoa no ecossistema Horizon.
  - `name` (String): Nome completo.
  - `identification_id` (String): Código anonimizado em conformidade com LGPD.
  - `classification` (String): Classificação institucional (`researcher`, `student`, `outside_ifes`).
  - `classification_confidence` (String): Nível de confiança da classificação (high, medium, low).
  - `classification_note` (String): Nota heurística de classificação.
  - `was_student` (Boolean): Flag indicando histórico prévio como discente.
  - `was_staff` (Boolean): Flag indicando vínculo como servidor/docente.
  - `cnpq_url` (String): Link do currículo na Plataforma Lattes.
  - `resume` (String): Resumo acadêmico do perfil.
  - `citation_names` (String): Formatos de citação bibliográfica.
  - `campus_id` (Int, FK -> `CAMPUS.id`, opcional): Campus principal de vinculação.

---

#### 16. `INICIATIVA_PESQUISA`
- **Fonte**: `horizon/initiatives_canonical.parquet` e aba `initiatives_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador da iniciativa de pesquisa no Horizon.
  - `name` (String): Título do projeto de pesquisa.
  - `status` (String): Situação atual (Active, Concluded, Cancelled).
  - `description` (String): Descrição ou resumo metodológico do projeto.
  - `start_date` (Datetime): Data oficial de início.
  - `end_date` (Datetime): Data oficial ou prevista de término.
  - `initiative_type_id` (Int, FK -> `TIPO_INICIATIVA.id`): Tipo de iniciativa.
  - `organization_id` (Int, FK -> `ORGANIZACAO.id`): Instituição responsável.
  - `parent_id` (Int, FK -> `INICIATIVA_PESQUISA.id`, autorrelacionamento): Projeto guarda-chuva.
  - `campus_id` (Int, FK -> `CAMPUS.id`, opcional): Campus vinculado.
  - `sigpesq_code` (String): Código original do projeto no SIGPesq (do bloco de enriquecimento).
  - `match_strategy` (String): Estratégia de correspondência do documento fonte.
  - `needs_review` (Boolean): Flag de necessidade de validação humana.
  - `linha_pesquisa` (String): Linha de pesquisa acadêmica extraída do SIGPesq.
  - `area_conhecimento_texto` (String): Descritor completo de área CNPq com código.

---

#### 17. `MEMBRO_EQUIPE_INICIATIVA` (Relação N:M)
- **Fonte**: Array `team` em `horizon/initiatives_canonical.parquet`.
- **Atributos**:
  - `initiative_id` (Int, FK -> `INICIATIVA_PESQUISA.id`)
  - `person_id` (Int, FK -> `PESSOA.id`)
  - `person_name` (String): Nome da pessoa na equipe.
  - `roles` (String / Array): Papéis exercidos (Coordinator, Researcher, Student).
  - `start_date` (Datetime): Entrada na equipe do projeto.
  - `end_date` (Datetime): Saída da equipe.

---

#### 18. `INICIATIVA_AREA_CONHECIMENTO` (Relação N:M)
- **Fonte**: Array `knowledge_areas` em `horizon/initiatives_canonical.parquet`.
- **Atributos**:
  - `initiative_id` (Int, FK -> `INICIATIVA_PESQUISA.id`)
  - `knowledge_area_id` (Int, FK -> `AREA_CONHECIMENTO.id`)

---

#### 19. `GRUPO_PESQUISA`
- **Fonte**: `horizon/research_groups_canonical.parquet` e aba `research_groups_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador do grupo de pesquisa.
  - `name` (String): Nome completo do grupo.
  - `short_name` (String): Sigla do grupo (ex.: ALMEC).
  - `description` (String): Linhas e foco de pesquisa.
  - `cnpq_url` (String): Espelho do grupo no Diretório CNPq.
  - `site` (String): Página oficial na web.
  - `organization_id` (Int, FK -> `ORGANIZACAO.id`): Organização responsável.
  - `campus_id` (Int, FK -> `CAMPUS.id`): Campus ao qual o grupo está sediado.

---

#### 20. `MEMBRO_GRUPO_PESQUISA` (Relação N:M)
- **Fonte**: Array `members` e `leaders` em `horizon/research_groups_canonical.parquet`.
- **Atributos**:
  - `group_id` (Int, FK -> `GRUPO_PESQUISA.id`)
  - `person_id` (Int, FK -> `PESSOA.id`)
  - `role` (String): Papel (Leader, Pesquisador, etc.).
  - `start_date` (Date): Início da participação no grupo.
  - `end_date` (Date): Término da participação.

---

#### 21. `GRUPO_AREA_CONHECIMENTO` (Relação N:M)
- **Fonte**: Array `knowledge_areas` em `horizon/research_groups_canonical.parquet`.
- **Atributos**:
  - `group_id` (Int, FK -> `GRUPO_PESQUISA.id`)
  - `knowledge_area_id` (Int, FK -> `AREA_CONHECIMENTO.id`)

---

#### 22. `ORIENTACAO`
- **Fonte**: Array `advisorships` em `horizon/advisorships_canonical.parquet` e aba `advisorships_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador da orientação acadêmica.
  - `name` (String): Título do plano de trabalho de orientação.
  - `status` (String): Situação (Concluded, Active).
  - `description` (String): Descrição ou programa vinculado.
  - `start_date` (Datetime): Data de início da orientação.
  - `end_date` (Datetime): Data de conclusão.
  - `person_id` (Int, FK -> `PESSOA.id`): Estudante orientado.
  - `supervisor_id` (Int, FK -> `PESSOA.id`): Docente orientador.
  - `fellowship_id` (Int, FK -> `PROGRAMA_BOLSA.id`, opcional): Modalidade de bolsa concedida.
  - `campus_id` (Int, FK -> `CAMPUS.id`, opcional): Campus vinculado.

---

#### 23. `ARTIGO` (Produção Bibliográfica)
- **Fonte**: `horizon/articles_canonical.parquet` e aba `articles_canonical` em `dicionarioHorizon.xlsx`.
- **Atributos**:
  - `id` (Int, PK): Identificador do artigo.
  - `title` (String): Título do artigo científico.
  - `doi` (String): Link DOI oficial.
  - `year` (Int): Ano de publicação.
  - `type` (String): Modalidade (Journal, Conference, etc.).
  - `journal_conference` (String): Periódico ou conferência de publicação.
  - `volume` (String): Volume da publicação.
  - `pages` (String): Paginação.
  - `campus_id` (Int, FK -> `CAMPUS.id`, opcional): Campus associado.

---

### 4.3. Tabelas de Governança, Linhagem e Auditoria (Horizon)

Essas tabelas registram todo o processo de ETL, deduplicação e resolução de entidades (*Entity Resolution*) do Horizon. Foram mantidas de acordo com suas fontes exatas:

#### 24. `GOVERNANCA_EXECUCAO_INGESTAO`
- **Fonte**: `horizon/ingestion_runs_canonical.parquet` e aba `ingestion_runs_canonical`.
- **Atributos**: `id` (Int, PK), `pipeline_name`, `run_status`, `source_system`, `input_snapshot_hash`, `started_at`, `finished_at`.

#### 25. `GOVERNANCA_MATCH_ENTIDADE`
- **Fonte**: `horizon/entity_matches_canonical.parquet` e aba `entity_matches_canonical`.
- **Atributos**: `id` (Int64, PK), `source_record_id` (Int64), `canonical_entity_type` (String), `canonical_entity_id` (Int64), `match_strategy` (String), `match_confidence` (String), `matched_at` (Datetime), `campus_id` (Int, FK -> `CAMPUS.id`).

#### 26. `GOVERNANCA_LOG_ALTERACAO`
- **Fonte**: `horizon/entity_change_logs_canonical.parquet` e aba `entity_change_logs_canonical`.
- **Atributos**: `id` (Int, PK), `ingestion_run_id` (Int, FK -> `GOVERNANCA_EXECUCAO_INGESTAO.id`), `source_record_id` (Int), `canonical_entity_type` (String), `canonical_entity_id` (Int), `operation` (String), `changed_fields_json` (String), `reason` (String), `changed_at` (Datetime).

#### 27. `GOVERNANCA_ASSERCAO_ATRIBUTO`
- **Fonte**: `horizon/attribute_assertions_canonical.parquet` e aba `attribute_assertions_canonical`.
- **Atributos**: `id` (Int, PK), `source_record_id` (Int), `canonical_entity_type` (String), `canonical_entity_id` (Int), `attribute_name` (String), `value_json` (String), `value_hash` (String), `is_selected` (Boolean), `selection_reason` (String), `asserted_at` (Datetime).

---

## 5. Recomendações e Oportunidades Técnicas Identificadas

Durante a varredura exaustiva dos dados locais, identificamos pontos técnicos valiosos para a integração prática entre os sistemas:
1. **Resolução de Entidades Pessoa (`PESSOA` <-> `EXTENSIONISTA`)**:
   - Como o Horizon já possui um mecanismo canônico de auditoria de matches (`entity_matches_canonical`) com estratégias como `canonical_name` e `normalized_name`, é viável construir uma pipeline de *Entity Resolution* automatizada para mapear `EXTENSIONISTA.slug` ao `PESSOA.id` utilizando a normalização de strings do atributo `nome`.
2. **Harmonização de Áreas de Conhecimento**:
   - A coluna `Grande área conhecimento (inferida)` e `Área temática` em `ACAO_EXTENSAO` pode ser mapeada diretamente para `AREA_CONHECIMENTO.id` (`knowledge_areas_canonical`), permitindo cruzar projetos de pesquisa e extensão por área temática e campus.
3. **Marts Analíticos Pré-calculados**:
   - O Horizon conta com arquivos como `advisorship_analytics.parquet` e `initiatives_analytics_mart.json`, e o SRC conta com `investimento.json` e `jornada.json`. Esses agregados representam *data marts* prontos para alimentar dashboards consolidados sem necessidade de reprocessar todo o grafo de relacionamentos a cada consulta.
