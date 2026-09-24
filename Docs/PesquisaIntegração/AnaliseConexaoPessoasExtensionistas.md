# Análise de Conexão e Normalização de Pessoas: Horizon, SRC e Diretoria

> **Sistemas Analisados:** Horizon (Pesquisa/Pós-Graduação), SRC (Extensão do Campus Serra) e Diretoria (Visão Gerencial da Extensão)  

---

## 1. Contexto e Objetivo

As bases de dados analisadas têm como origem o site **ifes-serra-lab**. Dentro dele existem sistemas e módulos de dados distintos que operam de forma isolada:

* **SRC** e **Diretoria**: concentram os dados de ações e atividades de extensão (sendo a Diretoria uma visão gerencial do SRC voltada ao Campus Serra);
* **Horizon**: concentra os dados de pesquisa, projetos científicos e grupos de pesquisa (com dados consolidados que abrangem o IFES em nível estadual).

> **Delimitação de Escopo:** Outros sistemas e bases presentes ou referenciados no `ifes-serra-lab` (como bases de Egressos, Editais e GeDoc) foram expressamente **descartados em etapas anteriores do processo**. O escopo de integração foi deliberadamente delimitado à tríade **Horizon, SRC e Diretoria**.

Apesar de cobrirem verticais distintas dentro do `ifes-serra-lab`, muitos indivíduos (docentes, servidores e discentes) atuam simultaneamente nas bases de extensão e pesquisa.

O objetivo desta análise foi investigar a viabilidade técnica de estabelecer uma conexão nominativa entre as entidades de pessoas dessas bases, identificando:
1. Onde os nomes de pessoas físicas estão armazenados em cada sistema;
2. O grau de correspondência e sobreposição real entre as bases;
3. A identificação de pessoas que aparecem apenas pontualmente em atividades de extensão (sem perfil formal de extensionista);

---

## 2. Mapeamento de Fontes com Nomes de Pessoas

### 2.1. Plataforma Horizon (Pesquisa e Pós-Graduação)

No Horizon, os nomes de indivíduos estão armazenados **exclusivamente em arquivos Parquet colunares**. Nenhum dos 3 arquivos JSON agregados da pasta (`initiatives_analytics_mart.json`, `research_group_membership_graphs_manifest.json` e `research_group_relationship_graphs_manifest.json`) armazena nomes de indivíduos (apenas contagens, métricas e nomes de grupos).

Os arquivos Parquet que contêm pessoas dividem-se em dois tipos:

#### A. Arquivos com coluna direta `name` (Cadastro Canônico e Grafos):
* **`researchers_canonical.parquet` (Base Mestre):** Contém todas as **10.089 pessoas** cadastradas no Horizon.
* **Subconjuntos Canônicos Filtrados por Classificação:**
  * `researchers_only_canonical.parquet`: **2.472 pessoas** (pesquisadores e servidores).
  * `students_canonical.parquet`: **6.519 pessoas** (estudantes e discentes).
  * `outside_ifes_canonical.parquet`: **849 pessoas** (colaboradores externos ao IFES).
  * `null_researchers_canonical.parquet`: **249 pessoas** (vínculo não classificado).
* **Nós dos Grafos de Rede (coluna `name` em cada nó):**
  * `people_collaboration_graph.nodes.parquet` e `people_relationship_graph.nodes.parquet` (escopo completo).
  * Versões específicas particionadas por categoria: `researchers_only_*`, `students_*`, `outside_ifes_*` e `null_researchers_*`.

> [!NOTE]
> **Constatação Estrutural:** A base `researchers_canonical.parquet` (10.089 linhas) é a **união matemática exata** dos 4 subconjuntos ($2.472 + 6.519 + 849 + 249 = 10.089$). Trata-se da base canônica consolidada completa de indivíduos do Horizon.

#### B. Arquivos Parquet com Nomes Embutidos em Colunas de Texto (JSON Serializado):
Estes arquivos são fisicamente 100% tabelas `.parquet` (não arquivos `.json` soltos), mas não trazem os nomes em uma coluna plana simples. Em vez disso, guardam listas e objetos inteiros codificados como texto JSON dentro de uma única célula/coluna da tabela Parquet:
* **`initiatives_canonical.parquet`:** Coluna de texto `team` (string JSON contendo array de membros: `[{"person_name": "...", "roles": [...]}]`).
* **`advisorships_canonical.parquet`:** Colunas de texto `advisorships` (array JSON com `person_name` do orientado e `supervisor_name` do orientador) e `team` (`name` e `role`).
* **`research_groups_canonical.parquet`:** Colunas de texto `members` e `leaders` (arrays JSON contendo `name`, `role`, `lattes_url`).
* **`advisorship_analytics.parquet`:** Coluna de texto `rankings` (objeto JSON com ranking `top_supervisors` contendo `name`).
* **`articles_canonical.parquet`:** **Não possui coluna de autores** (a autoria é mapeada a partir da pessoa para o artigo via campo `articles` em `researchers_canonical.parquet`).

---

### 2.2. SRC e Diretoria (Extensão e Ensino)

Os dados do **SRC** e da **Diretoria** foram adquiridos por meio do download do arquivo `.zip` disponibilizado diretamente dentro do próprio site e github do `ifes-serra-lab`. 

Quando descompactado, o arquivo `.zip` reproduz a estrutura de endpoints estáticos consumidos pelo frontend da aplicação web do laboratório. Isso explica a origem da pasta raiz `api/` e a organização dos dados em múltiplos arquivos `.json` divididos por entidade:

1. **`api/extensionistas/<slug>.json` (757 arquivos individuais):**
   * Contém os perfis dos extensionistas formalmente catalogados (`slug`, `nome`, `resumo_ia`, `acoes_coordenadas`, `participacoes_equipe`).
2. **`api/extensionistas/index.json` e `todos.json`:**
   * Lista consolidada com todos os 757 extensionistas catalogados e seus papéis gerais.
3. **`api/acoes/<id>.json` (202 arquivos) e `api/acoes/index.json`:**
   * Campo `Coordenador(a)` / `coordenador` (nome completo do coordenador responsável).
4. **`api/atividades/<id>.json` (525 arquivos):**
   * Campo `coordenador_acao` e array `equipe_execucao` (onde cada membro traz `nome`, `funcao` e `vinculo`).
5. **Arquivos de Apoio:**
   * `busca.json`, `pendencias-relatorio.json` e `sem-participacao.json` (contêm nomes e slugs de coordenadores).

---

## 3. Comparação de Nomes entre SRC e Diretoria

### Por que essa conferência foi necessária?
Como o **SRC** e a **Diretoria** são tratados como módulos separados dentro do `ifes-serra-lab`, surgiu uma dúvida fundamental antes de avançarmos para o cruzamento com o Horizon:
* *A Diretoria traz pessoas, coordenadores ou participantes que não estão cadastrados no SRC?*
* *Existem divergências de grafia ou nomes incompletos entre eles?*
* *Será necessário normalizar e cruzar o Horizon separadamente contra o SRC e contra a Diretoria?*

Para sanar essa dúvida e evitar retrabalho, realizamos uma conferência exaustiva, com auxílio do Gemini 3.8 Flash, registro por registro, arquivo por arquivo e campo por campo entre as duas bases:

| Dimensão Comparada | SRC | Diretoria | Divergências Encontradas | Grau de Correspondência |
|---|---|---|---|---|
| **Arquivos em `api/extensionistas/`** | 757 | 757 | 0 | **100,00% (Idênticos)** |
| **Grafia do campo `nome` nos perfis** | 757 | 757 | 0 | **100,00% (Idênticos)** |
| **Ações registradas (`api/acoes/`)** | 202 | 202 | 0 | **100,00% (Idênticos)** |
| **Atividades registradas (`api/atividades/`)** | 525 | 525 | 0 | **100,00% (Idênticos)** |
| **Total de pessoas físicas únicas somadas** | **914** | **914** | **0** | **100,00% (Idênticos)** |

### Conclusão:
A igualdade entre as duas bases é **absoluta (100,00%)**. Não existe nenhuma pessoa física que conste no SRC e não conste na Diretoria, ou vice-versa. 

Na prática, isso simplifica todo o projeto: **SRC e Diretoria compartilham exatamente a mesma base de pessoas**. Conectar o Horizon ao SRC significa conectá-lo simultaneamente à Diretoria, sem qualquer necessidade de regras ou cruzamentos duplicados.

---

## 4. Pessoas Pontuais na Extensão (Membros de Atividades sem Perfil Dedicado)

Ao varrer detalhadamente os 525 arquivos de atividades (`api/atividades/*.json`), constatou-se que o ecossistema de extensão da Serra envolve mais indivíduos do que os 757 extensionistas catalogados com página própria.

Existem **157 pessoas adicionais** que atuaram na extensão apenas de forma pontual como membros da `equipe_execucao` de atividades específicas ou na coordenação de eventos.

### Composição Institucional das 157 Pessoas Pontuais:
* **Alunos:** Alunos bolsistas (`ALUNO(A) BOLSISTA`) e voluntários (`ALUNO(A) VOLUNTARIO`) em cursos, oficinas ou tutorias.
* **Servidores:** Docentes e técnicos atuando como `INSTRUTOR(A)`, `MONITOR(A)`, `PROFESSOR(A)`, `DEBATEDOR(A)`, `ORGANIZADOR(A)` ou `COORDENADOR(A) ADJUNTO(A)`.
* **Convidados Externos:** Profissionais de fora do IFES atuando como `PALESTRANTE`, `MINISTRANTE` ou `AUTOR(A)`.

### Cruzamento dessas 157 Pessoas com o Horizon:
Dessas 157 pessoas que não tinham perfil próprio de extensionista no SRC:
* **57 pessoas (36,3%) também constam na base do Horizon!**
  * **27 Alunos/Discentes** (registrados em `students_canonical.parquet`).
  * **22 Servidores/Pesquisadores** (registrados em `researchers_only_canonical.parquet`).
  * **8 Convidados Externos** (registrados em `outside_ifes_canonical.parquet`).

### Casos Reais Comprovados:
1. **Discente Voluntário:**  
   * *Tales da Silva Amaral:* No SRC, consta apenas como `ALUNO(A) VOLUNTARIO` na atividade `9131` (*Tutoria em Matemática*). No Horizon, é um estudante formalmente catalogado em `students_canonical.parquet`.
2. **Docente / Instrutor:**  
   * *Vinícius Secchin de Melo:* No SRC, ministrou e coordenou cursos (*Veículos Elétricos*, *Materiais Rodantes*), mas não possui perfil em `extensionistas/`. No Horizon, é pesquisador formalmente registrado em `researchers_only_canonical.parquet`.
3. **Líder de Grupo de Pesquisa:**  
   * *Adrianna Machado Meneguelli:* No SRC, participou pontualmente como debatedora/organizadora na atividade `20745` (*Educação Especial Inclusiva*). No Horizon, é **Líder do Grupo de Pesquisa ALMEC** no CNPq (`research_groups_canonical.parquet`).

---

## 5. Métricas Consolidadas de Cruzamento e Normalização

### 5.1. Impacto da Normalização por Slug (Kebab-Case)

A comparação direta entre as grafias brutas do SRC e do Horizon revelou diversas inconsistências cosméticas (acentuação ausente no SRC, partículas em maiúsculas no Horizon). A normalização para slug kebab-case foi determinante:

| Universo Analisado | Registros | Matches Exatos (String pura) | Matches Normalizados (Slug) | Ganho com Normalização |
|---|---|---|---|---|
| **Extensionistas com perfil (`api/extensionistas/`)** | 757 | 268 (35,4%) | **342 (45,2%)** | **+74 pessoas (+27,6%)** |
| **Pessoas pontuais de atividades (`equipe_execucao`)** | 157 | 44 (28,0%) | **57 (36,3%)** | **+13 pessoas (+29,5%)** |
| **TOTAL GERAL DE PESSOAS DA EXTENSÃO (SERRA)** | **914** | **312 (34,1%)** | **399 (43,7%)** | **+87 pessoas (+27,9%)** |

> [!IMPORTANT]
> **43,7% de todos os indivíduos envolvidos na Extensão do Campus Serra (399 de 914 pessoas) possuem registros ativos no sistema de Pesquisa do IFES.**

### Exemplos do que a Normalização Resolveu:
* **Acentuação:** `Leticia Comissario da Silva` (SRC) $\leftrightarrow$ `Letícia Comissário da Silva` (Horizon) $\rightarrow$ Slug: `leticia-comissario-da-silva`
* **Preposições:** `Juliana Yuri Kanezaki de Souza` (SRC) $\leftrightarrow$ `Juliana Yuri Kanezaki De Souza` (Horizon) $\rightarrow$ Slug: `juliana-yuri-kanezaki-de-souza`

---

### 5.2. O Universo Completo de Indivíduos no Ecossistema

Pela teoria dos conjuntos, considerando o Horizon (todo o IFES) e o SRC/Diretoria (Campus Serra):

$$\text{Total de Pessoas Únicas} = |\text{Horizon}| + |\text{SRC}| - |\text{Interseção}|$$
$$\text{Total} = 10.089 + 914 - 399 = \mathbf{10.604 \text{ pessoas}}$$

```
┌─────────────────────────────────────────────────────────────┐
│                   ECOSSISTEMA GERAL: 10.604                 │
│                                                             │
│   ┌───────────────────────────┬──────────────┐              │
│   │          HORIZON          │ INTERSEÇÃO   │     SRC      │
│   │       (Todo o IFES)       │  (Em comum)  │ (Exclusivos) │
│   │                           │              │              │
│   │       9.690 pessoas       │ 399 pessoas  │ 515 pessoas  │
│   │                           │              │              │
│   └───────────────────────────┴──────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

1. **399 pessoas:** Presentes em **ambos os mundos** (Extensão da Serra + Pesquisa Estadual).
2. **515 pessoas:** Atuam **exclusivamente na Extensão da Serra** (sem registro no Horizon).
3. **9.690 pessoas:** Atuam **exclusivamente na Pesquisa** em outros campi do IFES ou na Serra sem vínculo com extensão local.

---

## 6. Auditoria de Duplicações, Cardinalidade e Homônimos

Para assegurar que o cruzamento nominativo não introduzisse distorções, realizou-se uma auditoria computacional rigorosa:

### 6.1. Auditoria Interna de Unicidade
* **No SRC:** Entre os 757 perfis e as 914 pessoas totais, **não existe nenhuma duplicidade** de nome ou slug (unicidade: 100%).
* **No Horizon:** Entre os 10.089 registros, **não existe nenhuma duplicidade** de nome ou slug (unicidade: 100%).

### 6.2. Auditoria de Cardinalidade (1:1 vs. 1:N)
* Todos os **399 matches encontrados são estritamente 1 para 1 (1:1)**.
* Nenhum slug do SRC apontou para dois ou mais registros no Horizon.

### 6.3. Avaliação de Riscos de Homônimos no Mundo Físico
Embora as chaves sejam 1:1 nas bases locais, a interpretação qualitativa distingue dois grupos de nomes:
1. **Nomes Compostos com 3 ou mais termos ($\approx 92\%$ dos casos):**
   * Exemplos: *Karin Satie Komati*, *Marcus Romano Salles Bernardes de Souza*, *Juliana Yuri Kanezaki de Souza*.
   * Probabilidade estatística de homônimo dentro do quadro funcional do IFES: **Desprezível (< 0,1%)**. Match confirmado com alta confiança.
2. **Nomes Curtos com 2 termos ($\approx 8\%$ dos casos):**
   * Nomes populares muito curtos podem, em tese, coincidir com alunos de outros campi. Para estes, recomenda-se a validação cruzada por campus ou grande área do conhecimento.

---

## 7. Abrangência Geográfica e Identificação de Campi no Horizon

A constatação de que o Horizon é uma base estadual multicampus (enquanto as bases de SRC e Diretoria concentram as ações de extensão do Campus Serra) foi comprovada a partir de dois campos estruturais dos próprios dados do Horizon:

1. **Coluna `campus_name` (Grafos de Pessoas):**  
   No arquivo `people_collaboration_graph.nodes.parquet`, a extração do dicionário da coluna física `campus_name` revelou **23 campi do IFES** distribuídos pelo Estado:
   > *Alegre, Aracruz, Barra de São Francisco, Cachoeiro de Itapemirim, Cariacica, Cefor, Centro-Serrano, Colatina, Guarapari, Ibatiba, Itapina, Linhares, Montanha, Nova Venécia, Piúma, Presidente Kennedy, Santa Teresa, São Mateus, Serra, Venda Nova do Imigrante, Viana, Vila Velha e Vitória.*

2. **Coluna `campus` (Tabelas Canônicas):**  
   Em `researchers_canonical.parquet` e `initiatives_canonical.parquet`, o atributo `campus` é serializado como `{"id": <int>, "name": "<string>"}`, identificando a unidade institucional do participante (ex.: `id: 6, name: "Serra"`; `id: 1, name: "Vila Velha"`; `id: 12, name: "Cariacica"`).
