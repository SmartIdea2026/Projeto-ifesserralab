---
description: Analisar e planejar integração de backends de projetos anteriores
---

# General Backend Integration Workflow

Este workflow auxilia na análise de projetos legados para propor e executar estratégias de integração com o projeto atual.

## Pré-requisitos
- Pasta contendo o código do projeto anterior (ex: `projetos_anteriores/`, `legacy/`, etc).

## Passos

### 1. Descoberta e Análise

// turbo
O agente deve explorar a estrutura do projeto legado para identificar a stack tecnológica:
- Liste as pastas de projetos anteriores.
- Identifique arquivos de configuração (ex: `requirements.txt`, `package.json`, `pom.xml`, `Dockerfile`).
- Determine a linguagem (Python, Node, Java, etc) e frameworks principais (Django, Flask, Express, Spring, Vanna.ai).

### 2. Avaliação de Viabilidade

Analise o código para responder:
- Existem regras de negócio reutilizáveis?
- O banco de dados pode ser aproveitado?
- Existe documentação (README, Swagger)?
- Qual a complexidade de refatoração vs reescrita?

### 3. Definição da Estratégia de Integração

Proponha uma das seguintes abordagens baseado na análise:
- **Wrapper API:** Criar uma nova API (ex: FastAPI/Express) que envolve o código legado.
- **Port:** Migrar a lógica para a linguagem/framework do novo projeto.
- **Microservice:** Rodar o legado como serviço containerizado independente.
- **Direct Import:** Importar módulos diretamente (se linguagens forem compatíveis).

### 4. Plano de Ação

Gere um plano passo-a-passo no `implementation_plan.md` do projeto atual:
1. Configuração do ambiente (dependências).
2. Estrutura de pastas sugerida (`backend/`, `database/`, `legacy_wrapper/`, etc).
3. Pontos de conexão (endpoints API, conexões DB).
4. Testes de validação.

### 5. Execução (Opcional)

Se aprovado pelo usuário, comece a criar a estrutura de pastas e arquivos de configuração necessários para a estratégia escolhida.

## Consumo de Contexto (Estimado)
- Modo: [LIGHT CONTEXT | NORMAL CONTEXT | HEAVY CONTEXT]
- Estimativa: ~[N]k tokens (ref: token_budget.md)
- Justificativa/Otimização: [Breve descrição]