# Modelo de Dados — SRC/Ifes

> **Sistema:** SRC — Sistema de Registro e Emissão de Certificados do Ifes  
> **Fonte:** Portal público + extração autenticada
> **Estrutura:** Banco de Dados Relacional Normalizado (PostgreSQL)

---

## Diagrama Entidade-Relacionamento (Físico)

```mermaid
erDiagram
    Pessoa {
        INT id PK
        VARCHAR nome
        VARCHAR cpf "PII"
        VARCHAR email "PII"
        VARCHAR vinculo
    }

    Acao {
        INT id PK
        VARCHAR processo UK
        VARCHAR titulo
        DATE data_cadastro
        BOOLEAN relatorio_aprovado
        VARCHAR url_detalhe
        INT fk_TipoAcao_id FK
        INT fk_Coordenador_id FK
        INT fk_Natureza_id FK
    }

    Atividade {
        INT id PK
        VARCHAR nome
        INT fk_Acao_id FK
        INT fk_TipoAtividade_id FK
    }

    TipoAcao {
        INT id PK
        VARCHAR nome
    }

    TipoAtividade {
        INT id PK
        VARCHAR nome
    }

    Natureza {
        INT id PK
        VARCHAR nome
    }

    Fomento {
        INT id PK
        VARCHAR nome
    }

    Campus {
        INT id PK
        VARCHAR nome
    }

    Funcao {
        INT id PK
        VARCHAR nome
    }

    AcaoVinculada {
        INT fk_AcaoVinculante_id FK
        INT fk_AcaoVinculada_id FK
    }

    FinanciamentoAcao {
        INT fk_Fomento_id FK
        INT fk_Acao_id FK
    }

    Local_Acao {
        INT fk_Campus_id FK
        INT fk_Acao_id FK
    }

    EquipeExecucao {
        INT fk_Pessoa_id FK
        INT fk_Atividade_id FK
        INT fk_Funcao_id FK
    }

    PublicoAlvo {
        INT fk_Pessoa_id FK
        INT fk_Atividade_id FK
        VARCHAR situacao
        FLOAT carga_horaria
        BOOLEAN certificado
    }

    %% Relacionamentos
    TipoAcao ||--o{ Acao : "categoriza"
    Natureza ||--o{ Acao : "classifica"
    Pessoa ||--o{ Acao : "coordena"
    
    Acao ||--o{ Atividade : "possui"
    TipoAtividade ||--o{ Atividade : "categoriza"

    Acao ||--o{ AcaoVinculada : "é vinculante de"
    Acao ||--o{ AcaoVinculada : "é vinculada a"

    Acao ||--o{ FinanciamentoAcao : "recebe"
    Fomento ||--o{ FinanciamentoAcao : "financia"

    Acao ||--o{ Local_Acao : "ocorre em"
    Campus ||--o{ Local_Acao : "sedia"

    Atividade ||--o{ EquipeExecucao : "executada por"
    Pessoa ||--o{ EquipeExecucao : "atua como"
    Funcao ||--o{ EquipeExecucao : "exerce"

    Atividade ||--o{ PublicoAlvo : "atende"
    Pessoa ||--o{ PublicoAlvo : "participa como"
```

## Dicionário de Tabelas

- **Pessoa**: Cadastro unificado de todas as pessoas (Coordenadores, Equipe e Público-Alvo). Usa deduplicação por CPF ou E-mail.
- **Acao**: A entidade central (Projetos, Cursos, Eventos). Contém os metadados públicos e é a raiz para todas as outras amarrações.
- **Atividade**: Turmas, módulos ou ações filhas diretas de uma Ação. Onde as pessoas realmente são alocadas.
- **Tabelas de Domínio (Lookups)**: `TipoAcao`, `TipoAtividade`, `Natureza`, `Fomento`, `Campus`, `Funcao`. Armazenam valores únicos para evitar redundância de strings.
- **Tabelas Associativas M:N**:
  - `AcaoVinculada`: Auto-relacionamento de Ações (Ação guarda-chuva / Ação filha).
  - `FinanciamentoAcao`: Relaciona uma Ação a múltiplos Fomentos e vice-versa.
  - `Local_Acao`: Relaciona uma Ação a múltiplos Campi e vice-versa.
  - `EquipeExecucao`: Relaciona a Pessoa, a Atividade e a Função (Membro da equipe).
  - `PublicoAlvo`: Relaciona a Pessoa e a Atividade guardando as métricas de conclusão (Carga horária, Situação, Certificado).
