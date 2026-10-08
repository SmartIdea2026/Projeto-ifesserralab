# Relatório de Análise: Modelo SQL Normalizado vs Atual

## 1. Visão Geral
Este relatório avalia a viabilidade e o impacto da substituição do modelo de banco de dados atual (utilizado na pipeline ETL em SQLAlchemy) pelo modelo lógico relacional proposto.

O modelo atual apresenta uma estrutura mais "plana" (denormalizada), ideal para rápida ingestão de dados extraídos de fontes JSON (como os arquivos no diretório `data/serra/`), onde campos como `campus`, `natureza` e `fomento` são armazenados como strings diretamente na tabela `Acao`.

O modelo proposto segue regras clássicas de normalização (3FN), separando atributos categóricos em tabelas de domínio (lookups/tipos) e criando relações mais explícitas.

---

## 2. É possível adaptar? Faz sentido?
**Sim, é plenamente possível e faz sentido**, mas depende do **objetivo** do banco de dados. 

Se o banco for usado para **sistemas transacionais (CRUD de uma aplicação web)**, a normalização proposta é excelente e recomendada.
Porém, como estamos tratando de um processo de extração (ETL - `src_etl`), a normalização introduz uma complexidade adicional na inserção dos dados, exigindo que o script resolva ou crie IDs (chaves estrangeiras) de tabelas auxiliares antes de inserir as ações e pessoas.

---

## 3. Pontos Positivos
* **Integridade Referencial e Consistência:** Impede que um "Campus" ou "Tipo de Ação" seja digitado de formas diferentes (ex: "Serra" vs "IFES-Serra"), pois haverá um cadastro único referenciado por ID.
* **Redução de Redundância:** Textos repetitivos como os nomes das naturezas e fomentos são substituídos por números (IDs INT), reduzindo o tamanho do banco.
* **Mapeamento de Relacionamentos Complexos:** A criação da tabela `Vinculacao` permite representar muito bem a hierarquia de ações (ação vinculante e vinculada), algo que existe na origem de dados mas não estava bem mapeado estruturalmente no modelo atual.
* **Coordenador Explícito:** Atribuir um `fk_Coordenador_id` diretamente na `Acao` facilita bastante as consultas, sem precisar varrer a equipe de execução procurando por uma função de "Coordenador".

---

## 4. Pontos Negativos e Alertas de Modelagem
* **Tamanho dos Campos (Muito Crítico):** O modelo proposto usa `VARCHAR(50)` para campos extensos. O título do projeto "Mulheres Mil – Eletricista Instalador Predial em Baixa Tensão" possui 61 caracteres, a `url_detalhe` possui quase 100 caracteres. Isso causará **erros de truncamento/inserção** no ETL. O atual usa até 500 caracteres.
* **Impacto no Processo de Ingestão (ETL):** O script em Python (`crud.py` / `pipeline.py`) terá que ser reescrito para, a cada inserção, verificar se o *Campus*, *Fomento* e *Natureza* existem no banco, inseri-los caso não existam, resgatar os IDs gerados e só então montar o registro de `Acao`.
* **Carga Horária no Público Alvo:** No modelo atual, a carga horária e vínculo estavam na `EquipeExecucao`. No modelo proposto, foi alocada em `PublicoAlvo`. Dependendo da regra de negócio, servidores/equipe executora também possuem carga horária registrada.
* **Perigo no `ON DELETE CASCADE`:** Vincular `ON DELETE CASCADE` a tabelas de domínio como `Campus` ou `Natureza` é perigoso. Se um campus for apagado acidentalmente, **todas as ações daquele campus sumirão**. O ideal para essas tabelas de classificação é usar `RESTRICT`.

---

## 5. Abordagens Mais Interessantes (Alternativas)

### A. Abordagem Analítica (Star Schema / Data Warehouse)
Dado que a stack atual envolve ETL e dados extraídos de painéis analíticos (`src_etl`), um banco fortemente normalizado pode não ser o melhor para relatórios. Uma abordagem **Star Schema (Modelo Dimensional)** seria criar tabelas Fato (cométricas, total de horas, inscritos) conectadas a tabelas Dimensão (Tempo, Geografia, Ação, Perfil da Pessoa). Isso facilita consultas em ferramentas como PowerBI e Metabase.

### B. Abordagem Híbrida (Recomendada)
Manter a agilidade do modelo atual, mas incorporando as melhores ideias do seu modelo:
1. **Adicionar a Tabela `Vinculacao`**: Essencial para conectar as ações matrizes às ações derivadas.
2. **Adicionar o `Coordenador` e `Campus`**: Como FKs diretas na `Acao` e na `Pessoa`.
3. **Manter as tabelas de tipos** (`TipoAcao`, `Natureza`, etc.) mas manter o fluxo do ETL resiliente (usando métodos de `get_or_create` no SQLAlchemy).
4. **Corrigir Tipagens**: Utilizar `VARCHAR(255)` ou `VARCHAR(500)` para Títulos e URLs.

---

## Próximos Passos
Posso ajudar a **refatorar o arquivo SQLAlchemy (`database.py`) atual** para incorporar o seu novo modelo lógico com as devidas correções de tamanhos de colunas e regras de deleção (CASCADE/RESTRICT), e ajustar os scripts ETL para suportar essa normalização. Gostaria de seguir por esse caminho?

