from sqlalchemy import text
from src_etl.etl import database

print("Dropando SCHEMA public (com CASCADE)...")
with database.engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE;"))
    conn.execute(text("CREATE SCHEMA public;"))
    conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    conn.commit()

print("Criando tabelas com o novo modelo normalizado...")
database.Base.metadata.create_all(bind=database.engine)
print("Banco de dados atualizado com sucesso!")
