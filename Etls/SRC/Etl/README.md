# Guia de Execução — ETL do SRC/Ifes

Este guia contém o passo a passo completo para configurar o ambiente e executar a extração de dados (ETL) do sistema SRC do Ifes localmente.

---

## 1. Pré-requisitos (O que instalar)

Antes de começar, garanta que você possui os seguintes softwares instalados na sua máquina:
- **Python 3.10 ou superior**
- **Docker e Docker Compose** (necessários para subir o banco de dados PostgreSQL)
- **Navegador Web** (para visualizar os dados via Adminer)

---

## 2. Configuração Inicial

### 2.1. Variáveis de Ambiente (Credenciais)
Para que o ETL consiga extrair dados sensíveis e restritos (como Equipe Executora e Público-Alvo), você precisa fornecer credenciais de acesso ao portal do SRC.
1. Na raiz do projeto, crie um arquivo chamado exatamente `.env`
2. Adicione as seguintes linhas com o seu login e senha do portal:
   ```env
   USER=seu_usuario_aqui
   PASSWORD=sua_senha_aqui
   ```
*(Nota: Se o `.env` não for criado, o ETL irá rodar parcialmente, extraindo apenas os dados públicos das Ações).*

---

## 3. Subindo a Infraestrutura de Banco de Dados

O banco de dados relacional e a ferramenta de visualização rodam via containers do Docker.

1. Abra o terminal na raiz do projeto.
2. Execute o comando abaixo para ligar o banco de dados e o Adminer em segundo plano:
   ```bash
   docker compose up -d
   ```
3. Se desejar limpar dados velhos ou (re)criar toda a estrutura de tabelas do zero seguindo o modelo atual, rode:
   ```bash
   venv/bin/python3 recreate_db.py
   ```

---

## 4. Executando o ETL

Com o banco de dados rodando e as credenciais configuradas, chegou a hora de raspar e popular os dados.

1. No terminal, execute o orquestrador principal:
   ```bash
   venv/bin/python3 run_etl_final.py
   ```
2. **Acompanhe o log**: O sistema irá abrir navegadores de forma invisível (*headless*), varrer as páginas do Campus configurado, resolver os relacionamentos (N:N) e fazer o UPSERT direto no PostgreSQL.
3. Aguarde até receber a mensagem `🏁 Processo de carga 100% Finalizado!`.

---

## 5. Visualizando os Dados

Para verificar os dados inseridos, testar queries ou exportar tabelas, use a interface web nativa (Adminer):

1. Acesse no navegador: [http://localhost:8080](http://localhost:8080)
2. Preencha as credenciais de banco:
   - **Sistema:** PostgreSQL
   - **Servidor:** `postgres`
   - **Usuário:** `etl_user`
   - **Senha:** `etl_password`
   - **Base de Dados:** `src_db`
3. Clique em "Comando SQL" para fazer consultas cruzando as entidades, por exemplo:
   ```sql
   -- Ver Ações e a qual Campus pertencem:
   SELECT a.titulo, c.nome AS campus 
   FROM acao a 
   JOIN local_acao la ON a.id = la."fk_Acao_id" 
   JOIN campus c ON la."fk_Campus_id" = c.id;
   ```

