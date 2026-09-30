# Documentação: Fontes de Dados e Scripts do ETL (Base SRC)

Este documento centraliza o mapeamento das fontes de dados utilizadas pelo ETL do SRC/IFES e lista os scripts em Python responsáveis por cada etapa do processo (Extração, Transformação e Consolidação).

---

## 1. Visão Geral do Pipeline

O fluxo completo do ETL pode ser representado da seguinte forma:

```mermaid
flowchart TD
    %% ==========================================
    %% 1. FONTES DE DADOS
    %% ==========================================
    subgraph Fontes["1. Fontes de Dados (Sistema do Ifes)"]
        SRC_PUB["Portal Público SRC<br/>(Sem Senha)"]
        SRC_PRIV["Portal Restrito SRC<br/>(Requer Login / .env)"]
    end

    %% ==========================================
    %% 2. EXTRAÇÃO DE DADOS
    %% ==========================================
    subgraph Extracao["2. Extração (Extract)"]
        subgraph ModulosPublicos["Extração Pública"]
            CLI_ETL([Comando: src-etl])
            SCR["scraper.py<br/>(Playwright: Lê a Tabela Geral)"]
            DET["detail.py<br/>(HTTPX: Puxa o HTML detalhado)"]

            CLI_ETL --> SCR
            CLI_ETL --> DET
        end

        subgraph ModulosPrivados["Extração Restrita"]
            CLI_PART([Comando: src-etl-part])
            GER["gerenciar.py<br/>(Playwright: Login e Busca)"]

            CLI_PART --> GER
        end
    end

    SRC_PUB --> SCR
    SRC_PUB --> DET
    SRC_PRIV --> GER

    %% ==========================================
    %% 3. ARMAZENAMENTO BRUTO
    %% ==========================================
    subgraph RawData["3. Arquivos Temporários (Raw Data)"]
        JSON_PUB[/"Arquivos JSON (Ações)<br/>Dados Básicos Públicos"/]
        JSON_PART[/"Arquivos JSON (Participações)<br/>Equipe + Público-Alvo"/]
    end

    SCR --> JSON_PUB
    DET --> JSON_PUB

    JSON_PUB -.->|Lê a lista de processos<br/>extraídos| CLI_PART
    GER --> JSON_PART

    %% ==========================================
    %% 4. TRANSFORMAÇÃO E ENRIQUECIMENTO
    %% ==========================================
    subgraph Transformacao["4. Transformação (Transform)"]
        CLI_ENR([Comando: src-etl-enrich])
        ENR["enriquecer.py<br/>(Limpeza e IA)"]
        API_MISTRAL(("API Mistral AI<br/>(Classifica Textos Vagos)"))

        CLI_VINC([Comando: src-etl-vinculadas])
        VINC["vinculadas.py<br/>(Mapeia Programa para Projeto)"]

        CLI_ENR --> ENR
        ENR <--> API_MISTRAL

        CLI_VINC --> VINC
    end

    JSON_PUB --> ENR
    ENR --> JSON_PUB_ENR[/"JSONs de Ações<br/>(Enriquecidos com IA)"/]
    JSON_PUB_ENR --> VINC
    VINC --> JSON_PUB_FINAL[/"JSONs de Ações<br/>(Hierarquia Completa)"/]

    %% ==========================================
    %% 5. CONSOLIDAÇÃO E CARGA
    %% ==========================================
    subgraph Consolidacao["5. Consolidação (Load)"]
        CLI_CONS([Comando: src-etl-consolidate])
        CONS["consolidar.py<br/>(Junta tudo)"]

        CLI_CONS --> CONS
    end

    JSON_PUB_FINAL --> CONS
    JSON_PART --> CONS

    CONS --> JSON_CONSOLIDADO[("serra_consolidado.json<br/>(Banco de Dados Único)")]

    %% ==========================================
    %% 6. SAÍDAS E RELATÓRIOS
    %% ==========================================
    subgraph Saidas["6. Geração de Relatórios (Outputs)"]
        PAINEL["src-etl-painel<br/>(Gera o Dashboard HTML)"]
        SITE["src-etl-site<br/>(Gera API e llms.txt)"]
        OUTROS["src-etl-export, relatorio-odt, etc<br/>(Planilhas e Docs)"]
    end

    JSON_CONSOLIDADO --> PAINEL
    JSON_CONSOLIDADO --> SITE
    JSON_CONSOLIDADO --> OUTROS

    %% ==========================================
    %% ESTILOS VISUAIS
    %% ==========================================
    classDef comando fill:#334155,stroke:#0f172a,stroke-width:2px,color:#fff;
    classDef fonte fill:#b91c1c,stroke:#7f1d1d,stroke-width:2px,color:#fff;
    classDef script fill:#0284c7,stroke:#0369a1,stroke-width:2px,color:#fff;
    classDef data fill:#ca8a04,stroke:#a16207,stroke-width:2px,color:#fff;
    classDef ia fill:#7c3aed,stroke:#5b21b6,stroke-width:2px,color:#fff;
    classDef final fill:#15803d,stroke:#14532d,stroke-width:3px,color:#fff;

    class CLI_ETL,CLI_PART,CLI_ENR,CLI_VINC,CLI_CONS comando;
    class SRC_PUB,SRC_PRIV fonte;
    class SCR,DET,GER,ENR,VINC,CONS script;
    class JSON_PUB,JSON_PART,JSON_PUB_ENR,JSON_PUB_FINAL data;
    class API_MISTRAL ia;
    class JSON_CONSOLIDADO final;
```

---

## 2. Fontes de Dados Mapeadas

Os dados consumidos pelo pipeline têm origens diferentes dentro do sistema SRC, dividindo-se entre áreas de acesso público e áreas que exigem autenticação institucional.

### 🔓 Fontes Públicas (Sem necessidade de login)

1. **Consulta Pública de Ações:**

   * **URL:** `https://src.ifes.edu.br/src/public/consulta-acao.xhtml`
   * **O que fornece:** Listagem completa e paginada de todas as ações de extensão e ensino registradas no campus. Fornece os IDs únicos (`acao_id`) necessários para as próximas etapas.
   * **Tecnologia de acesso:** Playwright (necessário para interagir com a interface JSF/PrimeFaces).

2. **Detalhe da Ação:**

   * **URL:** `https://src.ifes.edu.br/src/public/detalhe-acao.xhtml?id={acao_id}`
   * **O que fornece:** Dados descritivos da ação (Título, Tipo, Coordenador, Grande Área, Área Temática, Fomento, Processo).
   * **Tecnologia de acesso:** Requisição HTTP direta via `httpx`.

### 🔐 Fontes Autenticadas (Exigem login com credenciais do SRC)

3. **Gerenciamento de Público-Alvo:**

   * **URL:** `https://src.ifes.edu.br/src/pages/gerenciar/gerenciar-publico-alvo.xhtml?atividade={id}`
   * **O que fornece:** Dados quantitativos e nominais dos alunos atendidos (aprovados, certificados, situação). *Atenção: contém PII (Dados Pessoais).*
   * **Tecnologia de acesso:** Playwright mantendo sessão autenticada.

4. **Gerenciamento de Equipe de Execução:**

   * **URL:** `https://src.ifes.edu.br/src/pages/gerenciar/gerenciar-equipe-execucao.xhtml?atividade={id}`
   * **O que fornece:** Lista de professores, bolsistas e voluntários envolvidos na ação e suas funções.
   * **Tecnologia de acesso:** Playwright mantendo sessão autenticada.

### 🤖 Fontes Externas (APIs)

5. **Mistral AI (Opcional):**

   * **URL:** `https://api.mistral.ai/v1/chat/completions`
   * **O que fornece:** Inferência e preenchimento de campos de categorias que vêm vazios do SRC (Grande Área e Área Temática) baseando-se no título da ação.

---

## 3. Scripts do ETL Identificados

O código fonte (localizado na pasta `src/src_etl/etl/`) é dividido por responsabilidades claras.

### 📥 Extração (Extract)

* **`scraper.py`**: Interage com o portal público (Fonte 1), navega pelas páginas do campus e extrai os IDs das ações.
* **`detail.py`**: Acessa a página de detalhes de cada ação (Fonte 2) e converte o HTML em um dicionário de dados (título, coordenador, etc).
* **`gerenciar.py`**: Cuida do fluxo com login. Busca as ações pelo número do processo e extrai as participações e público-alvo (Fontes 3 e 4).

### 🔄 Transformação (Transform)

* **`models.py`**: Não executa extração, mas atua como a camada de tipagem e validação (Pydantic). Garante que todos os dados extraídos estejam no formato correto antes de serem salvos.
* **`enriquecer.py`**: Comunica-se com a API do Mistral (Fonte 5) para preencher categorias faltantes sem sobrescrever dados existentes.
* **`vinculadas.py`**: Resolve o auto-relacionamento entre ações, identificando quais ações são "programas guarda-chuva" e anexando as ações filhas a eles.

### 📦 Consolidação e Orquestração

* **`consolidar.py`**: O motor de junção. Lê os arquivos JSON de ações (gerados pelos scripts públicos) e os JSONs de participação (gerados pelos scripts autenticados) e mescla tudo em um único arquivo mestre (`serra_consolidado.json`).
* **`pipeline.py`**: O maestro do fluxo. Orquestra a ordem de execução, chamando o *scraper*, depois o *detail*, resolvendo os campi e paralelizando o trabalho via workers.
