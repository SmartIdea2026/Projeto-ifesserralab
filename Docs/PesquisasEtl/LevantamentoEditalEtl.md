# Levantamento do ETL de Editais

## 1. Introdução

Durante a investigação das fontes e dos scripts responsáveis pelos dados de Editais, o Portal de Editais direcionou inicialmente para o repositório [`portal_edital`](https://github.com/ifesserra-lab/portal_edital).

Entretanto, durante a análise desse repositório, não foram identificados os scripts responsáveis pela coleta e pelo processo de ETL dos dados.

A partir dessa investigação, foi localizado o repositório [`retrieve_edital`](https://github.com/ifesserra-lab/retrieve_edital), que contém a estrutura de ETL responsável pela coleta, transformação e persistência dos dados dos editais.

Dessa forma, o levantamento foi concentrado principalmente no `retrieve_edital`, utilizando também o `portal_edital` para compreender a utilização dos dados processados.

---

## 2. Repositórios Analisados

| Repositório | Responsabilidade Identificada |
|---|---|
| [`portal_edital`](https://github.com/ifesserra-lab/portal_edital) | Apresentação e disponibilização dos editais no portal |
| [`retrieve_edital`](https://github.com/ifesserra-lab/retrieve_edital) | Coleta, transformação e persistência dos dados dos editais |

---

## 3. Scripts e Fluxos de ETL Identificados

### Fluxos de ingestão

- `src/flows/ingest_fapes_flow.py`
- `src/flows/ingest_finep_flow.py`
- `src/flows/ingest_conif_flow.py`
- `src/flows/ingest_prppg_ifes_flow.py`
- `src/flows/ingest_proex_ifes_flow.py`
- `src/flows/ingest_capes_flow.py`
- `src/flows/ingest_cnpq_flow.py`
- `src/flows/ingest_horizon_flow.py`

### Execução e automação

- `scripts/run_all_flows.py` — execução dos fluxos de coleta.
- `.github/workflows/run_scraper.yml` — automação da execução dos fluxos.

### Transformação e normalização

- `src/components/transforms/edital_normalizer.py` — normalização dos dados coletados e transformação para a estrutura de edital.
- `src/components/transforms/publication_rules.py` — regras relacionadas à publicação e padronização dos dados.
- `scripts/curate_output.py` — curadoria e tratamento dos dados já persistidos.

### Persistência

- `src/components/sinks/json_sink.py` — persistência dos dados processados em arquivos JSON.

---

## 4. Fontes de Dados Identificadas

Os fluxos de ingestão identificados estão relacionados às seguintes fontes:

| Fonte | Fluxo |
|---|---|
| FAPES | `ingest_fapes_flow.py` |
| FINEP | `ingest_finep_flow.py` |
| CONIF | `ingest_conif_flow.py` |
| PRPPG/IFES | `ingest_prppg_ifes_flow.py` |
| PROEX/IFES | `ingest_proex_ifes_flow.py` |
| CAPES | `ingest_capes_flow.py` |
| CNPq | `ingest_cnpq_flow.py` |
| Horizon Europe | `ingest_horizon_flow.py` |

O Horizon Europe possui um fluxo próprio de ingestão, assim como as demais fontes identificadas.

---

## Processo Identificado

De forma simplificada, o processo de ETL encontrado segue a seguinte sequência:

`Fonte de dados` ➔ `Source` ➔ `Extração dos dados` ➔ `EditalNormalizer` ➔ `Regras de transformação / publicação` ➔ `LocalJSONSink` ➔ `data/output/*.json`

Os componentes de origem (`Source`) são responsáveis pela coleta dos dados de cada fonte. Após a extração, os dados passam pelo processo de normalização e pelas regras de transformação e publicação antes de serem persistidos em arquivos JSON.

---

## 6. Saídas e Controle do Processamento

As principais saídas e estruturas de controle identificadas são:

- `data/output/*.json` — dados dos editais processados.
- `registry/processed_editais.json` — controle dos registros já processados.
- `docs/flow_processing_log.md` — registro do processamento dos fluxos.

Também foram identificados mecanismos de controle de registros rejeitados durante o processamento.

---

## 7. Relação com os Dados do Portal de Editais

Os editais processados possuem informações utilizadas para sua organização e apresentação no Portal de Editais, incluindo:

- Órgão de fomento;
- Categoria;
- Status;
- Modalidade;
- Tags;
- Cronograma;
- Anexos.

Esses campos permitem que os editais sejam relacionados a diferentes elementos de organização do portal. O Horizon Europe, por exemplo, possui um fluxo próprio de coleta, e seus dados podem resultar em registros de editais associados a essa fonte.

O campo `órgão_fomento` não deve ser interpretado necessariamente como o nome do fluxo de ingestão, pois o processo de curadoria também pode determinar esse valor a partir de informações presentes no link do edital.

---

## 8. Relação entre `retrieve_edital` e `portal_edital`

O `retrieve_edital` concentra os processos de coleta e transformação dos dados, enquanto o `portal_edital` utiliza dados estruturados para disponibilizar os editais no site.

Durante o levantamento, foram identificadas estruturas de dados relacionadas entre os projetos. Entretanto, não foi identificada no código analisado uma etapa explícita que demonstre a transferência automática dos arquivos gerados pelo `retrieve_edital` para o `portal_edital`.

Essa relação pode ser investigada posteriormente caso seja necessário documentar o processo completo entre a coleta dos dados e sua disponibilização no portal.

---

## 9. Resultado do Levantamento

Foi localizado o repositório que contém os processos de ETL dos Editais, permitindo identificar:

- Os fluxos de coleta existentes;
- As fontes de dados de origem;
- Os componentes de transformação e normalização;
- As regras de publicação e curadoria;
- Os mecanismos de persistência;
- Os arquivos utilizados para controle do processamento;
- A relação dos dados processados com os elementos utilizados pelo Portal de Editais.
