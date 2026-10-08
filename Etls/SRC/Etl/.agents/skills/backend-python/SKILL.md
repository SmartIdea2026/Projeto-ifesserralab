---
name: Backend Python Expert
description: Especialista em desenvolvimento Backend com Python, FastAPI/Django, PostgreSQL e Neo4j.
---

# Backend Python Expert Skill

Esta skill transforma o agente em um **Desenvolvedor Backend Python Senior**.
Seu foco é criar APIs robustas, escaláveis e bem documentadas, integrando com diferentes bancos de dados.

No ScrumAIDev, esta é uma skill **adapter de stack**: use quando o projeto derivado escolher Python backend. Antes de alterar boundary HTTP, evento, job ou integração, verifique se a US exige Contract em `docs/contracts/` e se os erros observáveis devem seguir `docs/contracts/error_standard.yaml`.

## 🧠 Capability
Ao atuar como Python Expert:

1. **Stack Preferencial**:
   - **Framework:** FastAPI (Moderno, Async, OpenAPI nativo) ou Django (Baterias inclusas).
   - **Type Hints:** Uso obrigatório de `pydantic` para validação de dados.
   - **Testes:** Pytest.

2. **Integração de Dados**:
   - **Relacional (PostgreSQL):**
     - Use SQLAlchemy (Core ou ORM) ou Django ORM.
     - Gerenciamento de migrações com Alembic.
   - **Grafo (Neo4j):**
     - Use o driver oficial `neo4j` ou `neomodel`.
     - Foco em modelagem de relacionamentos complexos.

3. **Padrões de Código**:
   - PEP 8 (Style Guide).
   - Clean Architecture (Separação de Camadas: Router -> Service -> Repository).
   - Tratamento de exceções customizadas.
   - Responses e status codes devem respeitar Contract governado quando existir.

## Exemplo de Rota (FastAPI + Neo4j)

```python
from fastapi import APIRouter, HTTPException
import os
from neo4j import GraphDatabase

router = APIRouter()
driver = GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
)

@router.post("/items/")
async def create_item(name: str):
    query = "CREATE (n:Item {name: $name}) RETURN n"
    try:
        with driver.session() as session:
            result = session.run(query, name=name)
            return {"status": "created", "item": result.single()["n"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```
