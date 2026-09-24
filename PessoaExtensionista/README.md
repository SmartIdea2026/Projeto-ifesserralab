# ConexaoPessoaExtensionista

Normalização e cruzamento 1:1 de nomes de pessoas entre o ecossistema de **Extensão** (SRC e Diretoria do Campus Serra) e o de **Pesquisa** (Horizon) a partir das bases do [ifes-serra-lab](https://ifes-serra-lab.github.io/).

Cada pessoa recebe um **slug kebab-case** (minúsculas, sem acentos, sem caracteres especiais) e é cruzada contra o cadastro canônico do Horizon. O resultado registra a origem de cada indivíduo (SRC, DIRETORIA e/ou HORIZON) e separa quem tem vínculo com a pesquisa de quem é exclusivo da extensão.

**Resultado auditado:** 914 pessoas na extensão · 10.088 válidas no Horizon · **402 matches** (388 confirmados + 14 a validar) · 512 exclusivas da extensão · 9.686 exclusivas do Horizon.

---

## Estrutura

```text
ConexaoPessoaExtensionista/
├── scripts/        pipeline (7 módulos Python)
├── tests/          testes unitários e de integração (48 testes)
├── output/         os 5 JSONs gerados pela pipeline
├── docs/           governança: discovery, requirements, stories, tasks, sprint, backlog
├── requirements.txt
└── README.md
```

---

## Pré-requisitos

- Python 3.10+ (testado em Python 3.14.4)
- Dados de origem do ifes-serra-lab (veja seção **Dados de origem**)

## Preparar o ambiente

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Bibliotecas instaladas** (requirements.txt):

| Biblioteca | Versão | Uso |
|---|---|---|
| pandas | 3.0.6 | leitura do parquet do Horizon (`scripts/extracao_horizon.py`, `scripts/pipeline.py`) |
| pyarrow | 25.0.1 | backend de leitura do parquet |

O restante da pipeline usa apenas a biblioteca padrão do Python.

## Dados de origem

A pipeline espera a pasta `bases/` na raiz do projeto com esta estrutura:

```text
bases/
├── SRC/
│   └── api/
│       ├── extensionistas/
│       │   └── index.json          (757 extensionistas catalogados)
│       ├── atividades/             (525 arquivos *.json)
│       └── acoes/                  (202 arquivos *.json)
└── horizon/
    └── researchers_canonical.parquet
```

Se os dados ficarem em outro local, ajuste os caminhos em `scripts/caminhos.py`.

## Rodar a pipeline

```bash
python -m scripts.pipeline
```

Gera os 5 JSONs em `output/` e imprime o resumo do cruzamento no console:

| Arquivo | Conteúdo |
|---|---|
| `output/matches_confirmados.json` | pessoas presentes nas duas bases com 3+ termos no nome (388) |
| `output/matches_a_validar.json` | matches com nome curto de 2 termos, pendentes de validação humana (14) |
| `output/exclusivos_extensao.json` | pessoas só da extensão, sem match (512) |
| `output/exclusivos_horizon.json` | pessoas só do Horizon, sem match (9.686) |
| `output/resumo_auditoria.json` | universos, cruzamento, baseline da análise consolidada e desvios explicados |

## Rodar os testes

```bash
python -m unittest discover -s tests -t . -v
```

São 48 testes: unitários (funções puras de normalização, extração com fixtures temporárias e regras de negócio) e de integração (leitura das bases reais, contagens contra o baseline, geração dos arquivos e idempotência). Os testes de integração exigem a pasta `bases/` preenchida.

## Como o cruzamento funciona

1. **Extração** — 757 extensionistas catalogados (`extensionistas/index.json`) + pessoas pontuais de `coordenador_acao`/`equipe_execucao` das atividades + coordenadores de `Coordenador(a)` das ações (total 914, deduplicado por slug).
2. **Normalização** — nomes convertidos em slug kebab-case; partículas (`de/da/do/das/dos/e`) mantidas no slug mas excluídas da contagem de termos.
3. **Cruzamento** — join por slug contra o Horizon (exclusivamente `researchers_canonical.parquet`); matches com 2 termos vão para `matches_a_validar.json` (risco de homônimo).
4. **Auditoria** — unicidade de slugs, cardinalidade 1:1 e desvios vs a análise consolidada (399 esperados; 402 obtidos — diferença explicada no `resumo_auditoria.json`).

## Documentação

A pasta `docs/` guarda o processo completo: discovery, requirements (com o schema de cada JSON), 4 user stories com critérios de aceitação, task breakdowns, planejamento da sprint, product backlog e project manifest.
