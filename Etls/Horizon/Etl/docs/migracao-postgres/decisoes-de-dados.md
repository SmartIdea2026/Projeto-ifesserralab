# Decisões de dados da migração para PostgreSQL

Registro das decisões tomadas com o responsável durante a migração. "Antes" é o comportamento do ETL antigo; "Decisão" é o que o carregador novo faz.

## 1. Modelo e banco

| Tema | Antes | Decisão |
|---|---|---|
| `ModeloLogicoHorizon.sql` | Não existia | Fonte da verdade, **nunca editado**. O init traduz ao aplicar. |
| `DATETIME` | n/a | Vira `TIMESTAMP` em memória, antes do `CREATE TABLE`. |
| Ids | `INTEGER PRIMARY KEY` | `IDENTITY` em 18 tabelas (as que herdam o id da tabela-mãe ficam de fora). |
| Textos de 255 caracteres | SQLite não validava | 17 colunas de nome e título viram `TEXT`. |
| `bolsas` | `nome` único | `UNIQUE(nome, financiador_id)`, aplicado pelo init. |
| Recarga | `make db-reset` manual | Completa, 1º passo do pipeline. |
| Transação | Sessão única, rollback por linha | Savepoint por registro, commit por passo. |
| Rastreamento (5 tabelas) | Gravava com run context | Desligado; o código fica. |
| Exports, marts, relatório via sqlite3 | No pipeline | Fora do escopo; a reescrever. |
| Nomes | Inglês | Persistência nova em português; resto em inglês. |

## 2. Pessoas

| Tema | Antes | Decisão |
|---|---|---|
| `identificadores_pessoa` | Lattes no `cnpq_url` | Só `fonte='lattes'`. SigPesq e CNPq casam por e-mail e nome. |
| E-mail (LGPD) | Hash em todo e-mail, via hook do ORM | Hash em todos, **dentro do repositório**, idempotente. Perde o sinal `@ifes.edu.br`. |
| Proficiência | `ALTO`, `MEDIO`, `BASICO`, `NAO_SE_APLICA` | `alto`, `medio`, `basico`, `nao_se_aplica` (Bem, Razoavelmente, Pouco, outro). |
| `perfis_lattes.atualizado_em` | Não extraído | Lê `atualizacao_cv`; sem a data (ou sem resumo ou citações), o perfil é **pulado** e relatado. |
| Homônimo com outro ID Lattes | Trocava o ID da pessoa | Pessoa separada, e o caso vai para revisão. |
| Casamento do dono do Lattes | Pontuação por dados ligados | ID Lattes e depois o nome pelo `PersonMatcher`. |

## 3. Organizações, papéis e formação

| Tema | Decisão |
|---|---|
| IFES | Um registro só ("Instituto Federal do Espírito Santo", sigla IFES), nos dados iniciais. |
| Campus | Unidade do IFES. Grupo sem campus: "Campus Desconhecido"; grupo criado pelo projeto sem campus: "Reitoria". |
| Papéis de participação | `coordenador`, `pesquisador`, `estudante`, `orientador`, `orientando`. |
| Papéis de equipe | `lider`, `pesquisador`, `estudante`, `tecnico`. |
| Papel de vínculo | Campo `vinculo` do Lattes, criado sob demanda; atuação sem vínculo é pulada. |
| Tipo da organização | Instituição de formação: `instituicao_ensino`. Atuação profissional e demandante: regra pelo nome (ensino, órgão público ou empresa). Financiador: `fomento`. |
| Formação incompleta | Mantém os valores genéricos: "Unknown Institution", "Unknown", "Untitled", ano 0. |
| Orientador da formação | Lido da descrição ("Orientador:" e "Co-orientador:"), como antes. |

## 4. Equipes e áreas

| Tema | Decisão |
|---|---|
| Líder do SigPesq | Sem data de início (antes: a data da carga). |
| Papéis no grupo | A mesma pessoa pode ter vários papéis; repete-se só equipe + pessoa + papel. |
| Egresso (CNPq) | Papel base (pesquisador ou estudante) com `data_fim`; não há papel "(Egresso)". |
| Grupo citado só no projeto | Criado com os membros do projeto, como antes. |
| URL do CNPq já usada por outro grupo | Não gravada; vira pendência. |
| Áreas de conhecimento | Uma só normalização de nome para todas as fontes. |

## 5. Iniciativas

| Tema | Antes | Decisão |
|---|---|---|
| Identidade | Código no `metadata` (não gravado), depois nome | Dentro da execução; **com código, só o código casa** (títulos iguais com códigos diferentes viram iniciativas diferentes). |
| Organização | Sempre IFES | Campus de execução; sem campus, IFES. Pai provisório e Lattes: IFES. |
| Situação | `Active`, `Concluded`, `In Progress`, `Cancelled`, `Unknown`, texto cru | `em_andamento`, `concluida`, `cancelada`, `desconhecida`. Variações de "aprovado" seguem a data de fim; parecer vazio é `desconhecida`. |
| Filtro | Só parecer aprovado (SigPesq) | Mantido. |
| Tipos | `Research Project` e `Advisorship` | `projeto_pesquisa`, `projeto_extensao`, `projeto_desenvolvimento`, `orientacao`; o Lattes grava o tipo que traz. |
| Nome da orientação repetido | Sufixo "\| Orientacao aluno \| ano \| sigpesq id" | Mantido. |
| Projeto da equipe | Uma equipe por iniciativa | Pessoas em `participantes_iniciativa`; grupo SigPesq em `equipes_iniciativa` como `executor`. |
| Participantes | Removia os "obsoletos" | Só acrescenta. |
| Pai da orientação | Criado provisório | Mantido (IFES, `desconhecida`); datas e situação recalculadas no fim. |
| Lattes repetido | Sobrescrevia pelo nome | Junta por identidade ou nome exato **sem sobrescrever** (só preenche vazios e acrescenta participantes). |

## 6. Bolsas e financiamento

| Tema | Decisão |
|---|---|
| Identidade da bolsa | Programa + financiador. |
| Valor | Campo `Valor` da planilha de bolsistas; vazio grava 0. |
| Sem financiador | Bolsa pulada e relatada; a orientação continua. |
| `AgFinanciadora` | `organizacoes_iniciativa` como `financiadora`. |
| `ParceiroDemandante` | `organizacoes_iniciativa` como `demandante`. |
| Financiador do projeto Lattes | O primeiro vira `financiadora` (fomento). |
| Valor Aprovado (projeto) | **Descartado** e contado no relatório. |

## 7. Produções e documentos PJ

| Tema | Decisão |
|---|---|
| Congresso | Tipo próprio `trabalhos_completos_congressos`, também em `artigos`. |
| Artigo | Casa por DOI e depois por título + ano, entre currículos. |
| Sem ano ou veículo | Ano 0 e veículo "Não informado". |
| Link | `https://doi.org/<doi>`; sem DOI, vazio. |
| Coautores | Só os que casam com pessoa já existente (nome ou nome de citação, sem ambiguidade). |
| Documentos PJ | Preenchem descrição vazia e criam projeto para documento rico sem par (vai para revisão). O conteúdo extra é descartado. |
| Casamento por título aproximado | Gravado e listado em "revisar". |

## 8. Descartado de propósito (contado no relatório)

Valor Aprovado, grupo de pesquisa externo, conteúdo dos documentos PJ, dados de cancelamento do bolsista, tipo e instituição da orientação do Lattes, detalhes da atuação profissional.

## 9. Processo

Commits na `feat/32-horizon-etl-base`, sem trailer de IA e sem push; a partir da Etapa 5, automáticos ao fim de cada passo verificado.
