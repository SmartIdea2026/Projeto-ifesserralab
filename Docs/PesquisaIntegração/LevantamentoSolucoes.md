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

