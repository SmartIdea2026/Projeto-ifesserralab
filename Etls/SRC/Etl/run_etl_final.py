import os
from src_etl.etl import pipeline, database
from sqlalchemy import text

print("=========================================")
print("Iniciando ETL Completo (Ações + Participações)")
print("=========================================")

def print_log(msg):
    print(msg)

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

