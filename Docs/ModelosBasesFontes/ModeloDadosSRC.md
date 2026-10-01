# Modelo de Dados — SRC/Ifes

> **Sistema:** SRC — Sistema de Registro e Emissão de Certificados do Ifes  
> **Fonte:** Portal público + extração autenticada · Extração real: 200 ações (Campus Serra)  
> **Repositório ETL:** [ifesserra-lab/src](https://github.com/ifesserra-lab/src)

---

## Diagrama de Classes

```mermaid
classDiagram
    direction TB

    class Acao {
        +String acao_id PK
        +String processo UK
        +String titulo
        +String natureza
        +String tipo
        +String fomento
        +String grande_area
        +String area_tematica_principal
        +String area_tematica_secundaria
        +String campus
        +Date data_cadastro
        +Boolean relatorio_aprovado
        +String resumo
        +String url_detalhe
    }

    class Atividade {
        +String atividade_id PK
        +String num
        +String nome
        +String tipo
    }

    class MembroEquipe {
        +String nome
        +String funcao
        +String vinculo
        +Float carga_horaria
        +String cpf [PII]
        +String email [PII]
    }

    class ParticipantePublicoAlvo {
        +String nome
        +String situacao
        +String cpf [PII]
        +String email [PII]
    }

    class Extensionista {
        +String nome PK
        +String campus
        +List anos_ativos
        +Int total_atendidos
        +Int total_acoes
    }

    %% Relacionamentos
    Acao "0..1" --> "0..*" Acao : acao_vinculante
    Acao "1" *-- "0..*" Atividade : composta_por
    Acao "0..*" --> "1" Extensionista : coordenada_por

    Atividade "1" o-- "0..*" MembroEquipe : executada_por
    Atividade "1" o-- "0..*" ParticipantePublicoAlvo : atende_publico

    Extensionista "1" ..> "0..*" MembroEquipe : atua_como
```

---

## Dicionário de Dados

> Atributos que aparecem em mais de uma entidade são agrupados em uma única linha, com a coluna **Entidade(s)** identificando cada origem.  
> **Obrigatório** indica se o campo sempre tem valor preenchido no SRC — `Sim` significa que o ETL sempre o extrai; `Não` significa que pode vir vazio.
> 
> **O que significa PII?**  
> **PII** é a sigla para *Personally Identifiable Information*, ou **Informação de Identificação Pessoal**. São dados sensíveis que identificam uma pessoa real no mundo físico. Neste sistema, dados marcados como **Sim** na coluna PII (como CPF, e-mail e nomes de alunos) são protegidos, não sendo publicados na API aberta do painel e mantidos apenas na extração restrita local.

| Atributo | Entidade(s) | Tipo | Obrigatório | PII | Significado | Valores possíveis | Exemplo |
|---|---|---|---|---|---|---|---|
| `acao_id` | Acao | String (PK) | Sim | Não | Identificador numérico interno gerado automaticamente pelo SRC para cada ação cadastrada | Inteiro sequencial como string | `"5961"` |
| `processo` | Acao | String (UK) | Sim | Não | Número oficial do processo administrativo no padrão SIPAC/MEC. É a chave que conecta dados públicos e autenticados no ETL | Formato `NNNNN.NNNNNN/AAAA-DD` | `"23158.000507/2026-12"` |
| `titulo` | Acao | String | Sim | Não | Nome completo da ação exatamente como cadastrado pelo coordenador no SRC | Texto livre | `"ASAS - Operador de Computador"` |
| `natureza` | Acao | Enum | Sim | Não | Categoria acadêmica da ação — define se é extensão, ensino, pesquisa ou desenvolvimento institucional | `Extensão` · `Ensino` · `Pesquisa` · `Desenv. Institucional` | `"Extensão"` |
| `tipo` | Acao, Atividade | String | Sim | Não | Em **Acao**: modalidade formal da ação (Enum fechado). Em **Atividade**: classificação interna da atividade, menos padronizada (texto livre) | **Acao:** `Curso` · `Projeto` · `Evento` · `Programa` · `Programa em Rede` · `Prestação de Serviço` · **Atividade:** Texto livre | `"Curso"` |
| `fomento` | Acao | Enum | Sim | Não | Fonte de financiamento da ação. Indica se recebeu verba de programa governamental ou se é executada sem financiamento externo | `SEM VÍNCULO` · `PAEX-IFES` · `PRONATEC` · `MULHERES MIL` · `FAPES` · `SETEC` | `"PAEX-IFES"` |
| `grande_area` | Acao | Enum | Não | Não | Grande área do conhecimento (tabela CNPq) à qual a ação se vincula. Frequentemente vazio em ações antigas — pode ser inferido por IA via `src-etl-enrich` | `Ciências Exatas e da Terra` · `Ciências Biológicas` · `Engenharias` · `Ciências da Saúde` · `Ciências Agrárias` · `Ciências Sociais Aplicadas` · `Ciências Humanas` · `Linguística, Letras e Artes` | `"Engenharias"` |
| `area_tematica_principal` | Acao | Enum | Não | Não | Área temática de extensão principal (tabela Forproex/MEC). Define o eixo de impacto social da ação. Pode ser inferida por IA quando vazia | `Comunicação` · `Cultura` · `Direitos Humanos e Justiça` · `Educação` · `Meio Ambiente` · `Saúde` · `Tecnologia e Produção` · `Trabalho` | `"Tecnologia e Produção"` |
| `area_tematica_secundaria` | Acao | Enum | Não | Não | Segunda área temática de extensão, usada quando a ação cobre dois eixos temáticos ao mesmo tempo. Mesmo conjunto de valores da principal | Mesmo Enum de `area_tematica_principal` | `"Trabalho"` |
| `campus` | Acao, Extensionista | String | Sim | Não | Campus do Ifes vinculado à ação ou ao extensionista. Em **Extensionista** é derivado das ações em que participou | Texto livre | `"Serra"` |
| `data_cadastro` | Acao | Date | Sim | Não | Data em que a ação foi formalmente cadastrada no SRC pelo coordenador. Permite análise histórica por ano | `DD/MM/AAAA` | `"18/03/2026"` |
| `relatorio_aprovado` | Acao | Boolean | Sim | Não | Indica se o relatório final da ação foi submetido e aprovado. Armazenado como texto no SRC, não como booleano real | `"Sim"` · `"Não"` | `"Sim"` |
| `resumo` | Acao | String | Não | Não | Texto descritivo da ação escrito pelo coordenador. Descreve objetivos, metodologia e público. Usado pelo `src-etl-enrich` como entrada para classificação por IA | Texto livre longo | `"O Curso de Formação Inicial e Continuada (FIC)..."` |
| `url_detalhe` | Acao | String | Sim | Não | URL da página de detalhes da ação no portal público do SRC. Usada pelo ETL (`detail.py`) para buscar dados aprofundados via HTTPX | `https://src.ifes.edu.br/src/public/detalha-acao.xhtml?acao=<id>&pfdlgcid=<uuid>` | `"https://src.ifes.edu.br/.../detalha-acao.xhtml?acao=5961"` |
| `atividade_id` | Atividade | String (PK) | Sim | Não | Identificador numérico interno gerado automaticamente pelo SRC para cada atividade dentro de uma ação | Inteiro sequencial como string | `"1247"` |
| `num` | Atividade | String | Sim | Não | Número sequencial da atividade dentro da ação, exibido na interface do SRC. Serve para ordenação e identificação visual | Inteiro como string | `"1"` · `"2"` |
| `nome` | Atividade, MembroEquipe, ParticipantePublicoAlvo, Extensionista | String | Sim | Apenas em **ParticipantePublicoAlvo** | Nome descritivo ou nome completo da pessoa, conforme a entidade. Em **Atividade**: nome da atividade (público). Em **MembroEquipe**: crédito público, publicado. Em **ParticipantePublicoAlvo**: dado de identificação pessoal, nunca publicado. Em **Extensionista**: chave de identificação derivada | Texto livre | `"Turma 1"` · `"Felipe Frechiani de Oliveira"` · *(restrito em participante)* |
| `funcao` | MembroEquipe | Enum | Sim | Não | Papel desempenhado pelo membro na execução da atividade | `COORDENADOR(A)` · `PROFESSOR(A)` · `COLABORADOR(A)` · `PALESTRANTE` · `ORGANIZADOR(A)` · `ALUNO(A) BOLSISTA` · `ALUNO(A) VOLUNTARIO` · `ALUNO(A) EM ATIVIDADE CURRICULAR` | `"ALUNO(A) BOLSISTA"` |
| `vinculo` | MembroEquipe | String | Sim | Não | Vínculo institucional do membro com o Ifes — diferencia servidores efetivos, alunos e participantes externos à instituição | Texto livre | `"Servidor"` · `"Bolsista"` · `"Externo"` |
| `carga_horaria` | MembroEquipe | Float | Não | Não | Quantidade de horas dedicadas pelo membro à atividade. Registrada para fins de comprovante e relatório institucional | Número decimal | `40.0` |
| `cpf` | MembroEquipe, ParticipantePublicoAlvo | String | Não | **Sim** | CPF da pessoa. Coletado apenas na extração autenticada (`src-etl-part`). Usado para emissão de certificados. Nunca publicado na API pública | Formato `NNN.NNN.NNN-DD` | *(restrito)* |
| `email` | MembroEquipe, ParticipantePublicoAlvo | String | Não | **Sim** | E-mail da pessoa. Coletado apenas na extração autenticada. Usado para comunicação e envio de certificados. Nunca publicado na API pública | Formato e-mail padrão | *(restrito)* |
| `situacao` | ParticipantePublicoAlvo | Enum | Sim | Não | Status atual do participante em relação à atividade — se concluiu com aprovação, ainda está cursando ou foi reprovado | `APROVADO` · `CURSANDO` · `REPROVADO` | `"APROVADO"` |
| `anos_ativos` | Extensionista | List[String] | Sim | Não | Lista dos anos em que o extensionista coordenou ou integrou equipe de ao menos uma ação. Derivado de `data_cadastro` das ações relacionadas | Lista de strings de ano | `["2018", "2019", "2022"]` |
| `total_atendidos` | Extensionista | Integer | Sim | Não | Soma total de pessoas atendidas em todas as atividades das ações coordenadas ou integradas pelo extensionista. Derivado da contagem de `ParticipantePublicoAlvo` | Inteiro ≥ 0 | `247` |
| `total_acoes` | Extensionista | Integer | Sim | Não | Quantidade de ações em que o extensionista figura como coordenador responsável. Derivado da contagem em `Acao.coordenador` | Inteiro ≥ 1 | `9` |

