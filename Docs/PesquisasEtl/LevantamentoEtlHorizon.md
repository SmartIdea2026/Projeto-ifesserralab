#### **1\. Scripts e Fluxos de ETL (Pipelines) Identificados**

**SigPesq** 

* src/flows/sigpesq/projects.py  
* src/flows/sigpesq/groups.py  
* src/flows/sigpesq/advisorships.py  
* src/flows/sigpesq/enrich\_projects.py  
* src/flows/sigpesq/all.py

**Lattes**

* src/flows/lattes/download.py  
* src/flows/lattes/projects.py  
* src/flows/lattes/advisorships.py  
* src/flows/lattes/complete.py  
* src/flows/lattes/complete\_projects.py

**CNPq**

* src/flows/cnpq/groups.py

**Pipelines de orquestração**

* src/flows/pipelines/serra.py  
* src/flows/pipelines/unified.py  
* src/flows/pipelines/weekly.py  
* src/flows/pipelines/weekly\_orchestrator.py

**Scripts**

* scripts/cleanup\_fake\_identifications.py  
* scripts/cleanup\_legacy\_fellowships.py  
* scripts/debug\_list\_gen.py  
* scripts/init\_advisorship\_db.py  
* scripts/migrate\_resume.py  
* scripts/repair\_hash\_chains.py  
* scripts/scrub\_payload\_pii.py  
* scripts/seed\_test\_researcher.py  
* scripts/verify\_global\_sync.py  
* scripts/verify\_lattes\_parsing.py  
* scripts/verify\_mart.py  
* scripts/verify\_resume.py  
* **Estratégias de ETL Mapeadas no Código:**  
  * sigpesqprojectmappingstrategy: Estratégia de mapeamento de projetos.  
  * sigpesqexcelmappingstrategy: Processamento e extração a partir de relatórios locais em Excel.  
  * **Estratégias de Match/Desduplicação (Entity Matching):** canonical\_name, identity\_key, lattes\_id\_exact, doi\_exact, title\_year, natural\_key\_exact, cnpq\_group\_id, resolve\_or\_create\_researcher, normalized\_name.

**Saídas do ETL:** 

* **Entidades Canônicas:** campuses\_canonical.parquet, organizations\_canonical.parquet, initiative\_types\_canonical.parquet, knowledge\_areas\_canonical.parquet, fellowships\_canonical.parquet, articles\_canonical.parquet, initiatives\_canonical.parquet, research\_groups\_canonical.parquet, advisorships\_canonical.parquet.  
* **Recortes de Pessoas (Base Mãe pessoas\_canonical):** researchers\_canonical.parquet, students\_canonical.parquet, outside\_ifes\_canonical.parquet, null\_researchers\_canonical.parquet.  
* **Controle e Tracking do ETL:** entity\_tracking.parquet, ingestion\_runs\_canonical.parquet, entity\_change\_logs\_canonical.parquet, entity\_matches\_canonical.parquet.  
* **Analytics/Marts:** advisorship\_analytics, initiatives\_analytics\_mart, knowledge\_areas\_mart.

#### **2\. Fontes de Dados de Origem Mapeadas**

As informações que entram nos fluxos de ETL acima vêm das seguintes fontes brutas de origem:

* **SigPesq (Sistema de Gestão de Projetos de Pesquisa):** Fonte central explícita identificada como source\_system: sigpesq\_research\_projects e sigpesq\_research\_group. Os dados chegam ao ETL através de arquivos em formato planilha localizados em diretórios como data/raw/sigpesq/.  
* **Plataforma Lattes (CNPq):** Mapeada na fonte para a extração da URL dos currículos, chaves exatas de ID (lattes\_id\_exact) e validação de membros/pesquisadores em pessoas\_canonical e orientações.  
* **Diretório de Grupos de Pesquisa (DGP/CNPq):** Usada para mapear chaves como cnpq\_group\_id e a URL de espelho dos grupos de pesquisa registrados em research\_groups\_canonical.  
* **Bases com DOI/OpenAlex:** Identificada pela estratégia de busca doi\_exact nos matches do ETL, indicando consumo de catálogos acadêmicos externos para validação da base de articles\_canonical.
