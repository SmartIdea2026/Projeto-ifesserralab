# Análise das Fontes de Dados de Egressos

> **Escopo:** Foco nos dados de alunos (egressos) extraídos pelo linkedin. Dados salariais, estimativas de mercado e benchmarks externos estão fora da análise.

---

## 1. Fontes e campos analisados

### 1.1 Arquitetura do repositório

O repositório público clonado (`github.com/ifesserra-lab/egressos`) **não contém** o código de coleta nem os dados brutos com PII. Ele publica apenas o site estático e os JSONs já processados. A separação é intencional:

| Repositório | Conteúdo | Acesso |
|---|---|---|
| `ifesserra-lab/egressos-dados` (privado) | `alunos.json`, `perfis_linkedin.json`, `busca_egressos.py`, `busca_perfis.py`, `egressos_core/`, suíte de testes | Restrito |
| `ifesserra-lab/egressos` (público) | `pipeline/*.py` (orquestração), `dados/*.json` (outputs), HTML do site | Público |

Os scripts em `pipeline/` funcionam como **cascas de orquestração**: leem os dados, chamam funções do `egressos_core` e gravam os JSONs finais. A lógica de negócio está no `egressos_core`.

---

### 1.2 Fontes de dados dos alunos

Há dois universos de coleta, com processos distintos:

#### A) Coorte do Estudo Principal — 50 egressos do BSI

**Origem dos nomes:** base histórica do IFES Serra de alunos que passaram pelo tripé institucional (ensino/monitoria, pesquisa/IC com bolsa FAPES, extensão no LEDS e Morpheus Jr.).

**Coleta no LinkedIn:** feita pelo script `busca_egressos.py` (repo privado), usando:
- Google Chrome real com sessão autenticada no LinkedIn
- Framework [`browser-use`](https://github.com/browser-use/browser-use) para automação do navegador
- LLM Mistral Large como agente de extração

**Cruzamento com bases oficiais** (para cobrir períodos de bolsa que pessoas não publicam no LinkedIn):

| Base | O que fornece | Acesso |
|---|---|---|
| FAPES / PRODEST | Valores reais de bolsas de pesquisa (`relatorio_alocacao_bolsas.json`) | Restrito |
| SRC — IFES | Participação em projetos de extensão (`src_etl`) | Institucional |
| Lattes (CNPq) | Vínculos de IC, orientações, TCCs | Público |
| SIGPESQ (IFES) | Grupos de pesquisa, projetos, fellowships (`horizon.db`) | Institucional |

**Resultado final:** curadoria manual unificada no arquivo `alunos.json` (repo privado).

---

#### B) Coorte Ampliada — ~280 formandos de BSI e ECA

**Origem dos nomes:** exportação do **SIGA** (Sistema Integrado de Gestão Acadêmica do IFES).
- 170 formandos de BSI
- 110 formandos de ECA
- Gerado como fila `formandos_a_buscar`

**Coleta no LinkedIn:** feita pelo script `busca_perfis.py` (repo privado), em duas passadas:

1. **1ª passada — Identificação:** busca o nome no LinkedIn e verifica se a seção de Educação contém "IFES" ou "Instituto Federal do Espírito Santo". Extrai cabeçalho (cargo atual e empresa).
2. **2ª passada (`--trajetoria`):** entra no perfil confirmado e extrai o histórico completo de experiências.

Quando havia ambiguidade (nome duplicado ou LinkedIn bloqueou), o perfil ia para `perfis_conferidos.json` para **conferência humana** — um humano confirmava manualmente se era o aluno correto.

**Resultado:** gravado em `perfis_linkedin` (repo privado), consumido por `gen_cursos.py`.

---

### 1.3 Campos extraídos do LinkedIn (dado bruto reconstruído)

O arquivo `perfis_linkedin.json` (não disponível aqui por PII) tinha a seguinte estrutura, documentada pelos acessos `.get()` em `pipeline/gen_cursos.py`:

**Por aluno:**

| Campo | Tipo | Descrição |
|---|---|---|
| `nome` | `str` | Nome completo |
| `curso` | `"bsi"` \| `"eca"` | Curso de origem |
| `slug` | `str` | Identificador do perfil LinkedIn (`in/<slug>`) |
| `confirmado` | `bool` | Se a identidade foi verificada |
| `confirmado_por` | `str` | `"IFES lido"` (automático) ou `"conferência humana"` |
| `achado` | `bool` | Se o perfil foi localizado (independente de confirmação) |
| `falhou_a_rodada` | `bool` | Se o LinkedIn não carregou na rodada (perfil bloqueado, etc.) |
| `cargo_atual` | `str` | Cargo de destaque/headline |
| `empresa_atual` | `str` | Empresa atual |
| `local` | `str` | Localidade declarada no perfil |
| `headline` | `str` | Texto livre de apresentação — **descartado no ETL** |
| `experiencias` | `list` | Lista de posições profissionais (ver abaixo) |

**Por experiência (dentro de `experiencias`):**

| Campo | Tipo | Exemplo no bruto |
|---|---|---|
| `cargo` | `str` | `"Software Engineer -> -"` (com sujeira de seletor) |
| `empresa` | `str` | `"Vale"` |
| `tipo` | `str` | `"Full-time"` ou `"Integral"` (misto inglês/português) |
| `inicio` | `str` | `"Apr 2021"` (inglês textual, formato do LinkedIn) |
| `fim` | `str` \| `null` | `"Present"` ou `"Oct 2023"` (inglês textual) |
| `duracao` | `str` | `"5 yrs 5 mos"` (inglês textual) |
| `local` | `str` | `"Vitória, Espírito Santo, Brazil"` |
| `descricao` | `str` | Texto livre da vaga — **descartado no ETL** |

> **Fonte da reconstrução:** acesso `.get()` no código de `gen_cursos.py` (linhas 71–114) e docstring da função `_vitrine_da_coleta` (linhas 86–103), que lista explicitamente os exemplos de formato cru do LinkedIn.

---

## 2. Formato e estado dos dados

### 2.1 O que existe no repositório público

Nenhum dado bruto dos alunos está disponível no repo público. O que existe são **outputs pós-transformação**:

| Arquivo | Conteúdo | Estado |
|---|---|---|
| `dados/egressos_perfil.json` | 50 egressos do estudo: nome, cargo, empresa, local, jornada, senioridade, trilha | Transformado, publicável, sem renda |
| `dados/recorte_cursos.json` | Formandos do SIGA confirmados (BSI + ECA): nome, cargo, empresa, local, jornada | Transformado, publicável, sem renda |
| `dados/vitrine.json` | Perfis nomeados para a página "Onde estão os egressos" | Transformado, publicável |
| `dados/panorama.json` | Coorte de 50 anonimizada (label A–AX), com jornada e timeline | Anonimizado, sem nome |
| `dados/consolidado.json` | Série salarial estimada por egresso anonimizado | Anonimizado, sem nome |

### 2.2 Cobertura da coleta (números reais do `recorte_cursos.json`)

| Métrica | BSI | ECA |
|---|---|---|
| Formandos na fila (SIGA) | 170 | 110 |
| Processados pela coleta | 66 | 35 |
| Confirmados automaticamente | 33 | 11 |
| Confirmados por conferência humana | 31 | 17 |
| Aguardando conferência | 1 | 7 |
| Falhou na rodada (sem confirmação) | 1 | 0 |
| No estudo original (coorte de 50) | 50 | 0 |
| **Total identificados** | **114** | **28** |

---

## 3. Anomalias, regras e pontos de atenção

### 3.1 Limitações de acesso

- **ETL não é executável neste repo.** Depende de acesso ao `egressos_core` (pacote privado não publicado), dos arquivos de entrada PII (`alunos.json`, `perfis_linkedin.json`) e dos scripts de coleta (`busca_egressos.py`, `busca_perfis.py`).
- **`egressos_core` não está instalado.** A tentativa de `from egressos_core import dados` retorna `ModuleNotFoundError`.

### 3.2 Anomalias nos dados brutos (documentadas no código)

| Anomalia | Frequência documentada | Tratamento aplicado |
|---|---|---|
| Sujeira de seletor HTML no campo `cargo` (ex: `"-> -"`) | 20 em 150 posições da primeira coleta | Detectada por `jornada.plausivel()` e jornada inteira rejeitada |
| Datas e durações em inglês (`"Apr 2021"`, `"Present"`, `"5 yrs 5 mos"`) | Todas as posições da coleta automatizada | Traduzidas por `jornada.normaliza()` para `"2021-04"`, `null`, `"5 anos 5 meses"` |
| Tipo de contratação em idioma variável (`"Full-time"` vs `"Integral"`) | Frequente (misto) | **Não normalizado por decisão de projeto** — o vocabulário passa como veio |
| Aluno com nome idêntico a outra pessoa (homônimo) | Ocorrências não quantificadas | Encaminhado para `perfis_conferidos.json` + confirmação humana |
| LinkedIn bloqueou a leitura do perfil na rodada | 1 no BSI (documentado nas contagens) | Marcado como `falhou_a_rodada: true`; `busca_perfis.py --refazer` o retoma |

### 3.3 Regras de privacidade implementadas

- **Nenhum dado de aluno com nome vai para serviço externo de IA.** Apenas nomes de empresas (pessoas jurídicas) são enviados ao Mistral.
- **Dois campos de texto livre são sempre descartados:** `headline` e `descricao` — texto livre que pode conter comentários sobre terceiros não revisados.
- **Renda nunca acompanha nome.** O ETL produz dois arquivos separados: um com nome sem renda (`egressos_perfil.json`) e outro com renda sem nome (`renda_por_senioridade.json`). A separação é validada por teste automatizado.
- **Portão de PII no build:** `build_report.py` executa varredura em toda a saída antes de publicar — falha se qualquer nome real vazar.

### 3.4 Disponibilidade dos dados brutos

O dado mais próximo do bruto disponível neste repo é a vitrine em `recorte_cursos.json`. Porém, ele já passou por:
1. Filtragem (apenas perfis `confirmado: true` com `slug` válido entram)
2. Projeção de campos (apenas os 7 da `JORNADA_PUBLICA`, excluindo `headline` e `descricao`)
3. Normalização de datas e durações (do inglês para português e para `AAAA-MM`)
4. Limpeza de ruídos de HTML
5. Rejeição de jornadas com posições corrompidas (jornada inteira vira `[]`)

O **dado 100% bruto** (`perfis_linkedin.json`) está retido no repositório privado.


