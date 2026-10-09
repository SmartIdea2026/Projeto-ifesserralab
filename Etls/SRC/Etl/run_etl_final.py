import os
import sys
import time
from src_etl.etl import pipeline, database
from sqlalchemy import text

print("=========================================")
print("Iniciando ETL Completo (Ações + Participações)")
print("=========================================")

def print_log(msg):
    print(msg)

def preparar_banco(tentativas=30, intervalo=2):
    """Aguarda o PostgreSQL aceitar conexões e cria as tabelas (idempotente)."""
    ultimo_erro = None
    for i in range(1, tentativas + 1):
        try:
            with database.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            database.init_db()  # create_all: só cria o que ainda não existe
            print("✅ Banco de dados pronto (tabelas verificadas/criadas).")
            return
        except Exception as e:  # noqa: BLE001
            ultimo_erro = e
            print(f"⏳ Aguardando PostgreSQL ({i}/{tentativas})...")
            time.sleep(intervalo)
    print("❌ Não foi possível conectar ao PostgreSQL em localhost:5432.")
    print("   Suba o banco com: docker compose up -d")
    print(f"   Detalhe: {ultimo_erro}")
    sys.exit(1)

print("\n--- 0. Preparando banco de dados ---")
preparar_banco()

print("\n--- 1. Extraindo Ações do Campus Serra ---")
# Faz a raspagem pública e insere no modelo normalizado
pipeline.run(campus="Serra", headless=True, save_json=False, on_progress=print_log)

print("\n✅ Ações cadastradas/atualizadas no banco com sucesso!")

# Verifica se tem credenciais para buscar participacoes
tem_credenciais = False
if os.path.exists(".env"):
    with open(".env") as f:
        content = f.read()
        if "USER=" in content and "PASSWORD=" in content:
            tem_credenciais = True

if tem_credenciais:
    print("\n--- 2. Extraindo Participações ---")
    
    # Pega os processos recém-inseridos do banco
    db = database.SessionLocal()
    try:
        res = db.execute(text("SELECT DISTINCT processo FROM acao WHERE processo IS NOT NULL;"))
        processos = [row[0] for row in res.fetchall()]
    finally:
        db.close()
        
    print(f"Encontrados {len(processos)} processos únicos para buscar participações.")
    print("Iniciando workers paralelos...")
    
    # Usa 3 abas para ser mais rápido
    pipeline.run_participacoes(
        processos=processos,
        headless=True,
        save_json=False,
        on_progress=print_log,
        workers=3
    )
    print("\n✅ Participações (Equipes/Público-Alvo) cadastradas no banco com sucesso!")
else:
    print("\n⚠️ O arquivo .env não foi encontrado ou não possui USER/PASSWORD válidos.")
    print("A etapa de Participações (Equipe Executora e Público-Alvo) requer autenticação.")
    print("Foi ignorada por enquanto. Para executar, adicione as credenciais e rode novamente.")

print("\n🏁 Processo de carga 100% Finalizado!")

