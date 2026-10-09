import sys
from src_etl.etl import pipeline, database, models

def print_log(msg): print(msg)

print("Iniciando banco...")
database.init_db()
print("Testando pipeline (extrair 2 acoes)...")
dados = pipeline.run(campus="Serra", headless=True, max_acoes=2, on_progress=print_log)
print("Pipeline rodou.")
print("Acoes:", dados)
