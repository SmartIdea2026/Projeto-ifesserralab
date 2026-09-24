# Soluções para Integração das Bases SRC, Diretoria e Horizon — IFES

## Contexto do Problema

O IFES possui três bases de dados independentes que registram atividades acadêmicas (extensão e pesquisa), mas que **não compartilham um identificador comum**:

| Base | Domínio | Identificador de Pessoa | Identificador de Projeto |
|---|---|---|---|
| **SRC** | Extensão (front-end) | `slug` (texto: `pedro-abraao-lino-da-silva`) | `acao_id` (string: `"5357"`) |
| **Diretoria** | Extensão (API estática) | `slug` (texto) | `acao_id` (string) |
| **Horizon** | Pesquisa (modelo canônico) | `id` (inteiro: `372`) | `id` (inteiro: `81`) |

O mesmo professor que coordena um projeto de extensão no SRC e orienta um aluno de iniciação científica no Horizon aparece como **duas entidades distintas**, sem conexão. Isso impede análises integradas como: *"Quantos servidores atuam simultaneamente em pesquisa e extensão?"*.

**Restrição principal:** As bases originais **não podem ser modificadas**.

---

## Parte 1 — Estratégias de Cruzamento (como encontrar quem é quem)

### 1.1 Normalização + Slug Determinístico

**Descrição:** Transformar o campo `name` do Horizon no mesmo formato `slug` usado pelo SRC (minúsculas, sem acentos, hífens no lugar de espaços) e fazer um cruzamento exato.

**Exemplo com dados reais do projeto:**
```
Horizon:  name = "Karin Satie Komati"     → slug gerado = "karin-satie-komati"
SRC:      slug = "karin-satie-komati"     → MATCH EXATO ✅
```

**Prós:**
- Implementação trivial (10 linhas de Python)
- Zero ambiguidade — quando bate, é certeza (100% de precisão)
- Não requer bibliotecas externas
- Velocidade: cruza milhares de registros em milissegundos

**Contras:**
- Não tolera nenhuma variação (abreviação, erro de digitação, nome social vs. civil)
- Não diferencia homônimos (dois "João da Silva" em campi diferentes dariam match errado)
- Cobertura estimada: **~70-80%** dos registros

---

### 1.2 Fuzzy Matching (Similaridade Aproximada)

**Descrição:** Usar algoritmos matemáticos (Levenshtein, Jaro-Winkler, Token Sort) para calcular o grau de similaridade entre nomes que não bateram exatamente.

**Exemplo com dados reais do projeto:**
```
Horizon:  "Aline De Aguiar Lopes"
SRC:      "aline-aguiar-lopes"  (faltou o "de")

Jaro-Winkler:     95% de similaridade → MATCH ✅
Token Set Ratio:  100% (ignora palavras extras)
```

**Prós:**
- Resolve erros de digitação, preposições faltando ("de", "da", "dos") e capitalização
- Bibliotecas maduras disponíveis (`thefuzz`, `rapidfuzz` em Python)
- Pode definir nota de corte ajustável (ex: ≥ 90%)
- Cobertura adicional estimada: **~10-15%** dos registros restantes

**Contras:**
- Nomes curtos geram falsos positivos ("Ana Silva" ↔ "Ana Souza" = 80% similar, mas são pessoas diferentes)
- Custo computacional maior que slug exato (O(n²) se comparar todos contra todos)
- Requer definição humana da nota de corte — nota baixa = mais falsos positivos, nota alta = mais falsos negativos
- Necessita de biblioteca externa (`thefuzz` / `rapidfuzz`)

---

### 1.3 Desambiguação por Multi-Fatores

**Descrição:** Combinar múltiplos atributos para criar uma "impressão digital" da entidade. O match só acontece quando vários fatores coincidem simultaneamente.

**Exemplo com dados reais do projeto:**
```
REGRA: Pessoa A = Pessoa B se:
  (1) fuzzy(nome) ≥ 90%   E
  (2) mesmo campus         E
  (3) sobreposição de anos de atividade

Horizon: name="Carlos Roberto Pires Campos", campus="Vila Velha", ativo desde 2022
SRC:     slug="carlos-roberto-pires-campos", campus="Vila Velha", anos=["2023"]

Fator 1: match exato por slug ✅
Fator 2: campus "Vila Velha" = "Vila Velha" ✅
Fator 3: 2023 ∈ [2022..2026] ✅
→ MATCH COM ALTA CONFIANÇA ✅✅✅
```

**Fatores disponíveis para cruzamento de pessoas:**

| Fator | SRC / Diretoria | Horizon | Compatibilidade |
|---|---|---|---|
| Nome | `nome` (via slug) | `name` | ✅ Alta |
| Campus | `Campus` (na ação) | `campus.name` | ✅ Alta (ex: "Serra" = "Serra") |
| Papel/Função | `funcoes` = `["COORDENADOR(A)"]` | `classification` = `"researcher"` | ⚠️ Vocabulários diferentes |
| Anos ativos | `anos` = `["2015","2016"]` | `initiatives[].start_date` | ⚠️ Formatos diferentes |
| Área temática | `temas[].tema` | `knowledge_areas[].name` | ⚠️ Taxonomias diferentes |

**Fatores disponíveis para cruzamento de projetos:**

| Fator | SRC / Diretoria | Horizon | Compatibilidade |
|---|---|---|---|
| Título | `titulo` | `name` | ✅ Alta (fuzzy) |
| Campus | `Campus` = "Serra" | `campus.name` = "Serra" | ✅ Alta |
| Coordenador | `coordenador` (texto) | `team[].person_id` → `pessoa.name` | ✅ Via lookup |
| Área | `grande_area` | `enrichment.area_conhecimento` | ⚠️ Formatos diferentes |
| Ano | `ano` = "2013" | `start_date` = "2022-08-01" | ✅ Comparável |
| Processo | `processo` = "23158.000236/2025-14" | Não existe no Horizon | ❌ Sem correspondente |

**Prós:**
- Elimina praticamente todos os falsos positivos (homônimos em campi diferentes são filtrados)
- Quanto mais fatores coincidem, maior a confiança — resultado auditável
- Não requer machine learning nem treinamento
- Cobertura adicional estimada: **~5-8%** dos registros restantes

**Contras:**
- Mais complexo de implementar (lógica condicional com múltiplas regras)
- Depende da qualidade dos atributos secundários (muitos `null` no Horizon reduzem a eficácia)
- Requer conhecimento do domínio para definir quais combinações são confiáveis
- Pessoas que mudaram de campus entre os dois sistemas podem escapar

---

### 1.4 Machine Learning (Active Learning)

**Descrição:** Treinar um modelo de IA que aprende, a partir de exemplos rotulados por um humano, quais pares de registros representam a mesma entidade.

**Exemplo conceitual:**
```
O sistema apresenta pares ao usuário:
  Par 1: "Pedro Abraão Lino da Silva" (SRC) ↔ "Pedro Abraão L. Silva" (Horizon) → Humano: SIM
  Par 2: "Carlos Silva" (SRC) ↔ "Carlos Alberto Silva" (Horizon) → Humano: NÃO
  Par 3: "Ana Costa" (SRC) ↔ "Ana Costa" (Horizon, mesmo campus) → Humano: SIM
  ... repete 30-50 vezes ...
  
IA aprende os padrões e classifica os restantes automaticamente.
```

**Ferramentas open source disponíveis:** Dedupe.io, Zingg, Splink (criado pelo Ministério da Justiça do Reino Unido).

**Prós:**
- Maior precisão possível para dados com muita sujeira
- Aprende nuances que regras manuais não capturam (ex: abreviações de nome do meio)
- Escala para volumes maiores (milhares a milhões de registros)
- Modelos retreináveis conforme novos dados chegam

**Contras:**
- Requer rotulagem manual inicial (30-50 pares, ~1 hora de trabalho humano)
- Curva de aprendizado para configurar e treinar o modelo
- Dependência de bibliotecas especializadas
- Resultado probabilístico — sempre haverá uma margem de incerteza
- Pode ser excessivo para o volume de dados atual do IFES (milhares, não milhões)

---

### 1.5 MDM + Golden Record + Human-in-the-Loop

**Descrição:** Criar uma tabela mestra permanente (Golden Record) que registra todas as decisões de matching — automáticas e humanas — com rastreabilidade completa.

**Diferencial do projeto:** O Horizon **já possui a infraestrutura pronta** para isso. As tabelas `entity_matches_canonical` (com `match_strategy`, `match_confidence`, `canonical_entity_id`) e `entity_tracking` (com `entity_type`, `entity_id`, `sources`) são exatamente o padrão MDM.

**Exemplo de registro que seria criado:**
```json
{
    "id": 5001,
    "source_record_id": "pedro-abraao-lino-da-silva",
    "canonical_entity_type": "person",
    "canonical_entity_id": 47,
    "match_strategy": "slug_exact + campus_match",
    "match_confidence": 0.99,
    "matched_at": "2026-09-22T14:00:00Z"
}
```

**Fluxo operacional:**
```
Confiança ≥ 95%    →  Match automático (gravado direto)
Confiança 70-94%   →  Fila de revisão humana
Confiança < 70%    →  Descartado (não é a mesma entidade)
```

**Prós:**
- Solução definitiva e auditável (cada decisão tem registro de quem/como/quando)
- Infraestrutura já existe no Horizon (custo de implementação reduzido)
- Combina o melhor das abordagens automáticas com a segurança da revisão humana
- Escala no tempo (novos registros são processados pelo mesmo pipeline)
- Padrão de mercado reconhecido (MDM é disciplina formal de governança de dados)

**Contras:**
- Mais complexo de implementar (precisa do pipeline automático + interface de revisão)
- Requer alguém responsável pela curadoria contínua ("data steward")
- Depende de decisão institucional sobre quem é o "dono" do Golden Record
- Se a equipe for muito pequena, a revisão humana vira gargalo

---

## Parte 2 — Formas de Implementação (como construir na prática)

### 2.1 Script Python Puro

**Infraestrutura necessária:** Apenas Python (já disponível no servidor).

**Prós:**
- Zero dependência externa; implementável em 1-2 dias
- Resultado imediato (arquivo CSV/Excel com o de-para)
- Fácil de versionar no Git e compartilhar com a equipe
- Ideal para prova de conceito rápida

**Contras:**
- Execução manual — precisa rodar toda vez que os dados atualizam
- Sem interface visual — resultado é um arquivo, não um dashboard
- Difícil de manter se a lógica crescer muito

---

### 2.2 DuckDB (Banco Analítico Local)

**Infraestrutura necessária:** `pip install duckdb` (~20MB).

**Prós:**
- Lê JSON e Parquet nativamente, sem conversão prévia
- SQL é mais acessível para equipes diversas do que Python puro
- Arquivo `.duckdb` é portátil (copiar por pendrive, funciona em qualquer máquina)
- Performance excelente (milhões de linhas em segundos)
- Gratuito e open source

**Contras:**
- Ainda é execução manual (sem agendamento nativo)
- Sem interface gráfica própria (mas conecta em Power BI, Metabase etc.)
- Curva de aprendizado se a equipe não usa SQL

---

### 2.3 Jupyter Notebook (Exploratório + Documentado)

**Infraestrutura necessária:** `pip install jupyter pandas`

**Prós:**
- Cada passo fica documentado com texto, código e gráficos lado a lado
- Reproduzível — outra pessoa roda o mesmo notebook e chega ao mesmo resultado
- Ideal para apresentar a gestores, bancas ou comitês de governança
- Ótimo para um TCC, relatório técnico ou artigo acadêmico

**Contras:**
- Não é um sistema em produção — é uma análise pontual
- Precisa rodar manualmente a cada atualização
- Dependências Python (pandas, thefuzz)

---

### 2.4 Metabase + PostgreSQL (Dashboard Permanente)

**Infraestrutura necessária:** Servidor com Docker (ou VM simples) + PostgreSQL + Metabase (gratuito).

**Prós:**
- Dashboards acessíveis por qualquer pessoa via navegador (sem instalar nada)
- Atualização recorrente (agendar script ETL para rodar semanalmente/mensalmente)
- Metabase é gratuito e open source, com visual profissional
- Pode ser ampliado para incluir outros indicadores institucionais

**Contras:**
- Precisa de infraestrutura (servidor, Docker, manutenção)
- Mais complexo de montar inicialmente (1-2 semanas)
- Alguém precisa ser o administrador/dono do sistema
- Requer conhecimento de SQL e configuração de banco

---

### 2.5 dbt (Data Build Tool) — Pipeline Versionado

**Infraestrutura necessária:** PostgreSQL ou DuckDB + dbt-core (gratuito, open source).

**Prós:**
- Padrão de mercado para engenharia de dados moderna
- Pipeline versionado no Git — cada mudança fica registrada
- Testes automatizados ("garanta que não existem duplicatas no de-para")
- Documentação gerada automaticamente
- Escala para qualquer volume e complexidade

**Contras:**
- Curva de aprendizado moderada-alta (dbt tem conceitos próprios)
- Precisa de banco de dados por trás
- Investimento de 2-3 semanas para configurar
- Pode ser excessivo para um projeto com escopo limitado

---

## Parte 3 — Resumo Comparativo

### Estratégias de cruzamento

| Estratégia | Precisão | Cobertura estimada | Complexidade | Falsos positivos | Falsos negativos |
|---|---|---|---|---|---|
| Slug determinístico | 100% | ~70-80% | ⭐ | Nenhum | Muitos |
| Fuzzy Matching | ~90-95% | +10-15% | ⭐⭐ | Poucos (nomes curtos) | Poucos |
| Multi-Fatores | ~97-99% | +5-8% | ⭐⭐ | Raríssimos | Poucos |
| Machine Learning | ~98-99% | +2-3% | ⭐⭐⭐⭐ | Raríssimos | Raríssimos |
| MDM + Golden Record | ~99%+ (com humano) | 100% | ⭐⭐⭐ | Zero (revisado) | Zero (revisado) |

### Formas de implementação

| Implementação | Tempo | Custo | Mantém rodando? | Ideal para |
|---|---|---|---|---|
| Python puro | 1-2 dias | R\$ 0 | Não (manual) | Prova de conceito |
| DuckDB | 1-2 dias | R\$ 0 | Não (manual) | Equipe que prefere SQL |
| Jupyter Notebook | 2-3 dias | R\$ 0 | Não (manual) | Documentar e apresentar |
| Metabase + PostgreSQL | 1-2 semanas | R\$ 0 (open source) | Sim (agendável) | Dashboard permanente |
| dbt | 2-3 semanas | R\$ 0 (open source) | Sim (pipeline) | Engenharia de dados séria |

---

## Parte 4 — Recomendação para o Projeto IFES

### Estratégia de cruzamento recomendada: Pipeline em Cascata

Combinar as estratégias em sequência, do mais confiável ao mais tolerante:

```
PASSO 1 → Slug exato ........................ resolve ~75% dos matches
    ↓ (sobras)
PASSO 2 → Fuzzy ≥ 90% ...................... resolve ~15% adicionais
    ↓ (sobras)
PASSO 3 → Multi-fator (nome + campus + ano) . resolve ~8%
    ↓ (sobras: ~2%)
PASSO 4 → Revisão humana ................... resolve os 2% ambíguos
    ↓
RESULTADO → Gravado em tabela de-para (Golden Record)
```

### Implementação recomendada: Começar simples, evoluir depois

**Fase 1 (agora):** Python puro ou Jupyter Notebook → prova de conceito com resultado tangível em dias.

**Fase 2 (após validação):** Migrar para DuckDB ou PostgreSQL → persistir os resultados e conectar em Metabase para dashboards.

**Fase 3 (se o projeto crescer):** Adotar dbt para pipeline versionado e documentado, alimentando as tabelas de `entity_matches_canonical` do Horizon como Golden Record definitivo.

### Chave institucional — a solução definitiva

Se algum dia os dois sistemas (SRC e Horizon) passarem a registrar o **SIAPE** (matrícula do servidor federal) ou o **e-mail institucional (@ifes.edu.br)**, o problema de matching desaparece instantaneamente. Essa é uma decisão institucional, não técnica, mas vale registrar como recomendação de longo prazo.

---

## Parte 5 — Normalização de Nomes e Levantamento Inicial (SRC × Horizon)

Esta parte registra a abordagem definida para o **primeiro ciclo** de cruzamento de pessoas: normalizar o nome do Horizon no mesmo formato do `slug` do SRC e comparar por igualdade exata. Fuzzy matching, pontuação de confiabilidade e desempates ficam para ciclos seguintes, alimentados pelo que este levantamento mostrar.

### 5.1 O que foi verificado nos dados reais

**SRC e Diretoria são a mesma base.** A comparação entre o pacote `dados-abertos.zip` (SRC) e o repositório `ifesserra-lab/diretoria` (`docs/relatorios/campus-serra/api`) mostrou:

- os mesmos **757 extensionistas**, com os mesmos slugs e nomes, sem nenhum registro exclusivo de uma das bases;
- os **202 arquivos de ações e 525 de atividades idênticos byte a byte**;
- o `index.json` da Diretoria se descreve como "API estática do painel de Extensão — SRC/Ifes Campus Serra";
- o SRC tem **mais** campos (`atividades`, `temas`, `imp_coord`, `imp_eq`, `impacto` nos extensionistas; `investimento.json`, `jornada.json`, `temas.json` e o bloco `forproex` no painel), não dados diferentes.

**Consequência:** o SRC é usado como fonte única da extensão. A Diretoria não precisa ser cruzada; serve apenas como verificação automática de consistência (a Diretoria atualiza toda noite e o pacote do SRC toda semana, então pode haver alguns dias de defasagem).

**O `slug` do SRC é o próprio nome normalizado:**

| Verificação | Resultado |
|---|---|
| Slugs repetidos | 0 de 757 |
| Nome do arquivo = `slug` | 757 de 757 |
| `slug` = nome sem acento, minúsculo, com hífens | 757 de 757 (100%) |
| Slugs com sufixo de desempate (`-2`, `-3`) | 0 |
| Slugs com mais de uma grafia do nome nas ações/atividades | 0 |

Ou seja: o slug é único como chave de arquivo, mas **identifica um nome, não uma pessoa**.

### 5.2 Limitações do slug como identificador

- **Homônimos seriam fundidos sem aviso.** Como não há sufixo de desempate, duas pessoas diferentes com o mesmo nome cairiam no mesmo slug. Há **35 slugs com mais de um vínculo** (ex.: `adelson-pereira-do-nascimento` aparece 16× como Servidor e 7× como Aluno). A maioria deve ser a mesma pessoa que mudou de papel, mas os dados não permitem descartar homônimos.
- **Nem toda pessoa tem slug.** **157 nomes** aparecem na equipe de ações ou atividades sem ter arquivo em `extensionistas/`, incluindo 4 coordenadores de ação.
- **O slug muda se o nome mudar.** Uma correção de nome na origem gera outro slug na atualização seguinte. Por isso o nome original deve ser guardado junto com o slug.
- A mesma pessoa com dois slugs parece rara: apenas 2 pares suspeitos foram encontrados dentro do SRC e, pelos anos e colaboradores, são pessoas diferentes.

### 5.3 Por que campus e período não entram como desempate agora

- **Campus:** todos os dados atuais são do Campus Serra, então o campo não separa ninguém. Fica previsto como campo opcional para quando outros campi forem incluídos.
- **Período/anos:** registros da mesma pessoa vêm de bases diferentes, inseridos em momentos diferentes e por motivos diferentes. Os anos divergem mesmo quando a pessoa é a mesma, então usá-los como filtro geraria falsos negativos.
- **Vínculo (aluno/servidor ↔ `was_student`/`was_staff`):** pessoas mudam de papel ao longo do tempo. Pode servir no futuro apenas como sinal fraco, nunca como filtro.

O desempate mais promissor para ciclos futuros é a **rede de colaboradores** (colegas em comum já ligados), que não depende de campus nem de data.

### 5.4 Regra de normalização

A mesma função é aplicada ao `name` do Horizon e ao `nome` do SRC. Aplicada ao SRC, ela reproduz os 757 slugs existentes, o que valida a regra.

1. Decompor os caracteres Unicode (NFKD) e remover os acentos e a cedilha;
2. converter para minúsculas;
3. trocar toda sequência de caracteres não alfanuméricos por um único hífen;
4. remover hífens nas pontas.

```
Horizon: "Moises Savedra Omena"            → "moises-savedra-omena"
SRC:     "Adelson Pereira do Nascimento"   → "adelson-pereira-do-nascimento" (= slug existente)
```

Colunas derivadas previstas para os ciclos seguintes (não usadas no levantamento inicial): `tokens` (o slug separado por hífen, ex.: `["jose", "antonio"]`), `tokens_sem_particulas` (sem de/da/do/dos/das/e), `primeiro_nome`, `ultimo_nome` e `tokens_ordenados`.

### 5.5 Levantamento inicial: cruzamento exato

**Escopo:** apenas `slug` do SRC × nome normalizado do Horizon, por igualdade exata. Sem fuzzy, sem pontuação de confiabilidade, sem modelo probabilístico.

**Etapas:**

1. **Extração.** SRC: `api/extensionistas/todos.json` (`slug`, `nome`; 757 registros). Horizon: `researchers_canonical.parquet` (`id`, `name`; 10.089 registros, a base completa que contém os demais recortes).
2. **Normalização.** Gerar `slug_horizon` a partir de `name` com a regra da seção 5.4 e validar a regra contra os slugs do SRC.
3. **Diagnóstico de duplicidade.** Contar `slug_horizon` repetidos no Horizon (homônimos ou a mesma pessoa duplicada) antes de cruzar.
4. **Cruzamento.** Juntar SRC e Horizon pelo slug e classificar cada extensionista:

| Status | Significado |
|---|---|
| `casado_unico` | 1 extensionista ↔ 1 pessoa do Horizon |
| `casado_multiplo` | 1 extensionista ↔ várias pessoas do Horizon com o mesmo nome |
| `so_src` | extensionista sem correspondência no Horizon |
| `so_horizon` | pessoa do Horizon que não aparece no SRC (esperado para a maioria) |

5. **Saídas.**
   - `ligacao_src_horizon.json`: uma linha por extensionista, com `slug`, `nome_src`, `ids_horizon`, `nomes_horizon` e `status`;
   - `nao_casados_src.csv`: os `so_src` com o nome original, que serão a entrada do próximo ciclo;
   - `duplicados_horizon.csv`: nomes repetidos no Horizon;
   - resumo numérico: total do SRC, casados únicos, casados múltiplos, sem correspondência e duplicados no Horizon.
6. **Revisão rápida.** Olhar à mão cerca de 30 `so_src` para entender por que não casaram (acento, partícula, abreviação, sobrenome faltando ou pessoa ausente do Horizon). Os padrões encontrados definem o que o próximo ciclo precisa tratar.

**Ferramentas:** Python com `json`, `pandas` (`read_parquet` com `pyarrow`), `unicodedata` e `re`. Não há dependência de biblioteca de fuzzy matching nesta etapa.

```python
import json, re, unicodedata
import pandas as pd

def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

src = pd.DataFrame(json.load(open("api/extensionistas/todos.json")))[["slug", "nome"]]
assert (src["nome"].map(slugify) == src["slug"]).all()   # valida a regra

hor = pd.read_parquet("researchers_canonical.parquet", columns=["id", "name"])
hor["slug_horizon"] = hor["name"].map(slugify)

m = src.merge(hor, left_on="slug", right_on="slug_horizon", how="left")
g = m.groupby(["slug", "nome"]).agg(ids_horizon=("id", lambda x: [int(i) for i in x.dropna()]),
                                    nomes_horizon=("name", lambda x: list(x.dropna()))).reset_index()
g["status"] = g["ids_horizon"].map(lambda l: "so_src" if not l else "casado_unico" if len(l) == 1 else "casado_multiplo")
print(g["status"].value_counts())
g.to_json("ligacao_src_horizon.json", orient="records", force_ascii=False, indent=2)
```

### 5.6 Próximos ciclos (fora do escopo do levantamento inicial)

- comparação por tokens (ordem trocada, partículas e sufixos removidos) e fuzzy matching nos `so_src`;
- pontuação de confiabilidade para cada ligação;
- desempate pela rede de colaboradores para os `casado_multiplo`;
- criação do `id_unificado`, incluindo os 157 nomes sem slug e a marcação dos 35 slugs com vínculo misto como possíveis homônimos;
- revisão manual dos casos ambíguos, com as decisões registradas e reaplicadas a cada execução.
