# Modelo Conceitual — Portal de Editais

> Entidades e relacionamentos extraídos das bases JSON utilizadas pelo Portal de Editais.
> A pasta `data/` contém 58 arquivos JSON com a mesma estrutura de registro de edital.

---

## Diagrama ER

```mermaid
erDiagram

    EDITAL ||--o{ CRONOGRAMA : "possui"
    EDITAL ||--o{ ANEXO : "possui"
    EDITAL }o--o{ TAG : "possui"

    EDITAL {
        string nome
        string descricao
        string orgao_fomento
        string categoria
        string status
        string data_abertura
        string data_encerramento
        string link
    }

    CRONOGRAMA {
        string evento
        string data
    }

    ANEXO {
        string titulo
        string link
        string tipo
    }

    TAG {
        string nome
    }
```

# Entidades


| Entidade       | Descrição                               | Origem        |
| -------------- | --------------------------------------- | ------------- |
| **EDITAL**     | Informações principais do edital        | `data/*.json` |
| **CRONOGRAMA** | Eventos e prazos relacionados ao edital | `cronograma`  |
| **ANEXO**      | Documentos relacionados ao edital       | `anexos`      |
| **TAG**        | Palavras-chave associadas ao edital     | `tags`        |
