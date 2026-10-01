# Diagrama ER – Fonte SigPesq (Horizon ETL)

Tabelas, tipos, PKs e FKs conforme o schema do banco do Horizon (`db/horizon.db`, gerado pelo ETL `ifesserra-lab/horizon_etl`, commit `b45ac2f`). Atributos marcados `so na planilha` existem no SigPesq, mas o ETL não grava. O significado de cada tabela e atributo está no dicionário (`Dicionario_SigPesq.xlsx`).

```mermaid
erDiagram
    Organization {
        integer id PK
        varchar name
        varchar short_name
        text description
    }
    Campus {
        integer id PK
        varchar name
        varchar short_name
        integer organization_id FK
    }
    KnowledgeArea {
        integer id PK
        varchar name
    }
    Person {
        integer id PK
        varchar name
        varchar identification_id
        varchar celular "so na planilha"
    }
    PersonEmail {
        integer id PK
        integer person_id FK
        varchar email
    }
    Researcher {
        integer id PK, FK
    }
    Role {
        integer id PK
        varchar name
        text description
    }
    Team {
        integer id PK
        varchar name
        varchar short_name
        text description
        integer organization_id FK
    }
    ResearchGroup {
        integer id PK, FK
        integer campus_id FK
        varchar cnpq_url
        varchar site
        varchar parecer_diretoria "so na planilha"
    }
    TeamMember {
        integer id PK
        integer person_id FK
        integer team_id FK
        integer role_id FK
        datetime start_date
        datetime end_date
    }
    InitiativeType {
        integer id PK
        varchar name
        text description
    }
    Initiative {
        integer id PK
        varchar name
        varchar status
        text description
        datetime start_date
        datetime end_date
        integer initiative_type_id FK
        integer organization_id FK
        integer parent_id FK
        text enrichment_json "JSON dos documentos PJ"
        varchar sigpesq_project_code "so na planilha"
        varchar parecer_diretoria "so na planilha"
        varchar natureza "so na planilha"
        boolean sigilo "so na planilha"
        varchar linha_pesquisa "so na planilha"
        varchar knowledge_area "so na planilha"
        varchar external_partner "so na planilha"
        varchar external_research_group "so na planilha"
        varchar parceria_polo_inovacao "so na planilha"
        integer qtd_pts "so na planilha"
        integer qtd_financiamentos "so na planilha"
        integer qtd_outros "so na planilha"
    }
    Advisorship {
        integer id PK, FK
        integer fellowship_id FK
        boolean cancelled
        date cancellation_date
        varchar sigpesq_workplan_code "so na planilha"
        integer sigpesq_id "so na planilha"
        integer ano "so na planilha"
        varchar edital "so na planilha"
        varchar modalidade "so na planilha"
        varchar gerenciamento "so na planilha"
        float value "so na planilha"
        varchar curso "so na planilha"
        varchar campus_name "so na planilha"
        varchar area_conhecimento "so na planilha"
        varchar grade_area "so na planilha"
        varchar cancelled_by "so na planilha"
        boolean aceite_orientador "so na planilha"
        datetime aceite_orientador_data "so na planilha"
        boolean aceite_orientado "so na planilha"
        datetime aceite_orientado_data "so na planilha"
        boolean ciente "so na planilha"
        varchar avaliacao_relatorio "so na planilha"
    }
    AdvisorshipMember {
        integer id PK
        integer advisorship_id FK
        integer person_id FK
        integer role_id FK
        varchar role_name
        date start_date
        date end_date
    }
    Fellowship {
        integer id PK
        varchar name
        text description
        float value
        integer sponsor_id FK
    }
    LattesECnpq {
        varchar fonte "outras fontes do Horizon"
    }
    Organization ||--o{ Campus : possui
    Campus |o--o{ ResearchGroup : sedia
    Organization |o--o{ Team : "dona de"
    Team ||--o| ResearchGroup : "e um (mesmo id)"
    Team ||--o{ TeamMember : "tem membros"
    Role |o--o{ TeamMember : "papel de"
    Person ||--o{ TeamMember : participa
    Person ||--o{ PersonEmail : tem
    Person ||--o| Researcher : "e um (mesmo id)"
    LattesECnpq }o..o{ Person : "tambem alimenta Person, ResearchGroup e Initiative"
    Organization |o--o{ Initiative : executa
    InitiativeType |o--o{ Initiative : classifica
    Initiative |o--o{ Initiative : "projeto pai"
    Initiative }o--o{ Team : initiative_teams
    Initiative ||--o| Advisorship : "e um (mesmo id)"
    Organization |o--o{ Fellowship : patrocina
    Fellowship |o--o{ Advisorship : financia
    Advisorship ||--|{ AdvisorshipMember : "aluno e orientador"
    Role |o--o{ AdvisorshipMember : "papel de"
    Person ||--o{ AdvisorshipMember : participa
    KnowledgeArea }o--o{ ResearchGroup : group_knowledge_areas
    KnowledgeArea }o--o{ Initiative : initiative_knowledge_areas
    KnowledgeArea }o--o{ Researcher : researcher_knowledge_areas
```

**Legenda**

| Ponta da linha | Significado |
| --- | --- |
| dois traços | exatamente um |
| círculo + traço | zero ou um |
| traço + pé de galinha | um ou vários |
| círculo + pé de galinha | zero ou vários |

Linha cheia: chave estrangeira no banco. Linha tracejada: outras fontes do Horizon (Lattes e CNPq). Linhas com nome de tabela (`initiative_teams`, `*_knowledge_areas`) são tabelas de ligação N:N. "e um (mesmo id)" indica herança: a tabela usa o mesmo id da outra.
