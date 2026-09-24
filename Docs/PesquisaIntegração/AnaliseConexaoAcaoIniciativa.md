

## 1. Sumário Executivo

Este documento apresenta a validação técnica e conceitual da integração entre as **Ações do SRC** (focadas prioritariamente em Extensão e Ensino no Campus Serra) e as **Iniciativas do Horizon** (focadas em Pesquisa e P&D em todo o Ifes).

A análise utilizou comparação textual estrita e fuzzy matching via algoritmo **Ratcliff-Obershelp** (`difflib.SequenceMatcher`), seguida de validação semântica cruzando coordenadores, equipes e resumos.

### Principais Indicadores
* **Ações SRC analisadas:** 201 registros.
* **Iniciativas Horizon analisadas:** 4.737 registros brutos (4.572 após deduplicação).
* **Ações do SRC com correspondência direta por nome ($\ge 0{,}85$):** **58 ações (28,86% do total)**.
  * No recorte de **Extensão**, a cobertura direta atinge **49,54%** (54 de 109 ações).
* **Total de pares consolidados:** **72 conexões diretas** (47 relações 1:1 e 11 relações 1:N).

---

## 2. Metodologia de Validação e Critérios de Similaridade

### 2.1. Pré-processamento e Normalização Textual
Para garantir que variações superficiais não impedissem correspondências legítimas, os títulos passaram por:
1. **Case-folding:** Conversão total para maiúsculas.
2. **Remoção de pontuação e caracteres especiais:** Substituição de travessões (`–`), hífens (`-`), dois-pontos (`:`), barras (`/`) e parênteses por espaços simples.
3. **Colapso de espaços em branco:** Eliminação de espaços múltiplos e trims nas extremidades.

### 2.2. Algoritmo de Similaridade
Utilizou-se o algoritmo `SequenceMatcher.ratio()`, que calcula a razão entre os caracteres correspondentes nos maiores blocos contíguos comuns ($M$) e o total de caracteres de ambas as cadeias ($|A| + |B|$):

$$S = \frac{2 \times M}{|A| + |B|}$$

* **Linha de corte adotada:** **$S \ge 0{,}85$**.
* **Justificativa do corte:** Em testes empíricos, scores abaixo de $0{,}80$ introduziram falsos positivos provocados por termos acadêmicos genéricos recorrentes (*"Estudo de"*, *"Introdução a"*, *"Laboratório de"*). Acima de $0{,}85$, 100% dos pares manuais conferidos tratavam-se, de fato, do mesmo projeto.

---

## 3. Análise de Conexões e Relações (Critério de Aceitação 1)

### 3.1. Validação Semântica: Os nomes realmente batem e se referem às mesmas coisas?
**Sim.** A conferência qualitativa entre o `Resumo` do SRC e a `description` / `team` do Horizon confirmou que os 72 pares referem-se aos mesmos projetos institucionais, compartilhando o mesmo escopo técnico, público-alvo e participantes.

Exemplos de correspondência exata ($S = 1{,}00$):
* **SRC #4830** `ConectaFapes: Uma plataforma de apoio à Pesquisa...` $\leftrightarrow$ **Horizon #751**
* **SRC #3140** `LAMPEX – Laboratório Modelo de Práticas de Extensão` $\leftrightarrow$ **Horizon #3403**
* **SRC #3567** `Laboratório IFMaker Serra: um ambiente colaborativo...` $\leftrightarrow$ **Horizon #3471**
* **SRC #4034** `SmartIdea - Validação de Problemas e Ideias` $\leftrightarrow$ **Horizon #3584**

### 3.2. Padrões de Mapeamento e Dependências

#### A. Relações 1:1 (47 ações)
Uma única ação do SRC mapeia diretamente para uma única iniciativa do Horizon. São projetos de ciclo único ou finalizados.

#### B. Relações 1:N (11 ações do SRC gerando 25 links no Horizon)
Ocorrem quando uma ação unificada no SRC possui múltiplos registros legítimos no Horizon decorrentes de:
1. **Fases e Continuidade Temporal (Versões I, II, III):**
   * *Exemplo:* A ação **SRC #1834** (*Sistema para predição de transtornos mentais...*) vincula-se à iniciativa base (**HZ #3590**), à fase seguinte (**HZ #3587 - Fase II**) e ao projeto de modelagem teórica (**HZ #261**).
   * *Exemplo:* A ação **SRC #645** (*SIPAC*) conecta-se a **HZ #1150** (versão 1) e **HZ #4683** (*SIPAC2*).
2. **Modalidades de Execução:**
   * *Exemplo:* A ação de Pré-Incubação do SRC vincula-se tanto à modalidade de *Competências Empreendedoras* quanto à modalidade de *Residência* no Horizon.

### 3.3. Diferenças e Variações Encontradas entre os Sistemas
As divergências observadas entre os títulos são de quatro naturezas:
1. **Prefixos de Escopo no Horizon:** O Horizon adiciona prefixos contextuais como *"Projeto APEXT 2026..."* (em vez de apenas *"APEXT 2026..."*) ou *"Curso de Extensão do GAIn: Introdução..."*.
2. **Singular vs. Plural:** Variações como *"Competência Empreendedora"* (SRC) vs. *"Competências Empreendedoras"* (Horizon).
3. **Erros de Digitação na Origem:** Ex.: Horizon #3544 registrou *"NTELIGENTE"* sem o "I" inicial em *ESPM-Empregos*.
4. **Duplicações Internas no Horizon:** Foram detectados **157 grupos de nomes duplicados (322 iniciativas envolvidas)** no Horizon geradas por ingestões simultâneas de fontes distintas (PDFs do SigPesq vs. cadastros manuais). **A deduplicação é pré-requisito mandatório.**

### 3.4. O que ocorre com as 143 Ações do SRC sem correspondência de título?
As 143 ações restantes não possuem projetos irmãos diretos porque:
* 33 são **Eventos** pontuais (jogos, simpósios, semanas comemorativas) que não constituem projetos de pesquisa/P&D.
* 82 são ações de **Ensino** (tutorias curriculares, nivelamento em matemática, cursos de idiomas básicos).
* **Conexão via Pesquisador:** Verificou-se que **83,9% (120 ações)** dessas ações sem match de título foram coordenadas por docentes que estão ativamente cadastrados como pesquisadores no Horizon, viabilizando uma integração por vínculo de autoria/docente.

---

## 4. Regras de Negócio, Restrições e Impactos no Fluxo (Critério de Aceitação 2)

### 4.1. Regras de Negócio (RN)

* **RN01 - Normalização e Limiar Mínimo:**  
  Qualquer rotina automatizada de vinculação por título deve normalizar strings (remover pontuações, converter para maiúsculas e colapsar espaços) e exigir score de similaridade $S \ge 0{,}85$. Vínculos entre $0{,}70$ e $0{,}84$ não devem ser automáticos; devem ser direcionados para fila de aprovação humana.

* **RN02 - Suporte à Cardinalidade 1:N com Qualificação de Vínculo:**  
  O modelo de dados deve permitir que uma `Ação_ID` do SRC aponte para uma lista de `Iniciativa_ID` do Horizon. Cada vínculo deve possuir um metadado de tipo de relação (ex.: `FASE_SEGUINTE`, `SUBPROJETO`, `VERSAO_PARALELA`).

* **RN03 - Deduplicação Obrigatória da Tabela de Iniciativas:**  
  Antes de vincular iniciativas ao SRC, o sistema deve resolver a chave canônica no Horizon. Se existirem IDs duplicados para o mesmo projeto no Horizon (mesmo nome normalizado e mesma equipe), a ligação deve ser associada preferencialmente ao registro canônico ativo mais recente.

* **RN04 - Estratégia de Mapeamento em Cascata (Fallback):**  
  Para cobrir os casos onde o título não coincide:
  1. *Camada 1:* Match de Título ($S \ge 0{,}85$) $\rightarrow$ Vínculo direto de Projeto.
  2. *Camada 2:* Match de Coordenador/Equipe + Grande Área Temática $\rightarrow$ Vínculo de Linha de Ação/Pesquisador.

### 4.2. Restrições e Limitações (RT)

* **RT01 - Assimetria de Escopo dos Sistemas:**  
  O Horizon cobre exclusivamente projetos de pesquisa e desenvolvimento tecnológico de todo o Ifes. O SRC cobre projetos, cursos, oficinas e eventos extensionistas do Campus Serra. A expectativa de cobertura direta por título nunca atingirá 100% da base do SRC (teto estimado em torno de ~40% a ~50%).
* **RT02 - Metadados de Campus Incompletos no Horizon:**  
  No Horizon, apenas 68 iniciativas possuem a tag literal do campus *"Serra"*, enquanto 4.664 registros estão sem identificação explícita de unidade. A amarração com o SRC supre essa lacuna e permite georreferenciar pelo menos 72 iniciativas adicionais ao Campus Serra.

### 4.3. Impactos no Fluxo de Negócio e Arquitetura (IF)

1. **Pipeline de Ingestão e ETL:**  
   Necessidade de um estágio de enriquecimento pós-carga que aplique o dicionário de correspondências (`conexoes_src_horizon_72_pares.json`), gravando uma foreign key ou tabela associativa `src_acao_horizon_iniciativa`.
2. **Visualização Unificada (Dashboard Institucional):**  
   Possibilidade de exibir, na visualização de uma Ação de Extensão, as publicações científicas, patentes e orientações que decorreram da iniciativa no Horizon.
3. **Indicadores de Indissociabilidade (Ensino-Pesquisa-Extensão):**  
   O mapeamento destas 58 ações fornece evidência auditável de indissociabilidade entre pesquisa e extensão, permitindo relatórios automáticos para o Ministério da Educação (MEC) e órgãos de fomento (FAPES/CNPq).

---

## 5. Estrutura do Arquivo de Entrega

O artefato com os pares confirmados foi consolidado no arquivo JSON:
* **Local:** `bases/conexoes_src_horizon_72_pares.json`
* **Esquema:**
```json
{
  "score_similaridade": 1.0,
  "src": {
    "acao_id": "string",
    "titulo": "string",
    "natureza": "string",
    "tipo_acao": "string",
    "coordenador": "string"
  },
  "horizon": {
    "iniciativa_id": 0,
    "nome": "string",
    "status": "string",
    "coordenador": "string"
  }
}
```

---

## 6. Conclusão

A validação conclui que **a conexão por título é viável, altamente confiável e recomendada**, cobrindo praticamente metade (49,54%) de todas as ações de extensão registradas no Campus Serra. 

As inconsistências e duplicações observadas no Horizon foram isoladas e tratadas, garantindo um conjunto limpo de 72 vínculos diretos suportados por regras de negócio claras e prontos para homologação e carga em banco de dados.
