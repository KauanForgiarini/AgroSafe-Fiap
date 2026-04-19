"""
=============================================================
  AgroSafe — Setup do Banco de Dados Oracle
  Execute UMA vez para criar a estrutura no banco.
=============================================================
  Pré-requisito: pip install oracledb
  Configurar variáveis de ambiente antes de executar:
    ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN
=============================================================
"""

import os

try:
    import oracledb
except ImportError:
    print("❌ Pacote 'oracledb' não encontrado.")
    print("   Instale com: pip install oracledb")
    exit(1)

DDL_TABELA = """
CREATE TABLE agrosafe_perdas (
    id             NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data_hora      VARCHAR2(30)   NOT NULL,
    fazenda        VARCHAR2(100)  NOT NULL,
    cultura        VARCHAR2(50)   NOT NULL,
    fase           VARCHAR2(30)   NOT NULL,
    area_ha        NUMBER(10,2)   NOT NULL,
    perda_kg_ha    NUMBER(10,2)   NOT NULL,
    prejuizo_rs    NUMBER(15,2)   NOT NULL,
    classificacao  VARCHAR2(20)   NOT NULL
)
"""

DDL_INDEX = """
CREATE INDEX idx_agrosafe_fazenda ON agrosafe_perdas(fazenda)
"""

def setup():
    user     = os.getenv("ORACLE_USER",     "rm12345")
    password = os.getenv("ORACLE_PASSWORD", "senha123")
    dsn      = os.getenv("ORACLE_DSN",      "oracle.fiap.com.br:1521/orcl")

    print(f"Conectando em: {dsn} com usuário: {user}")
    try:
        conn = oracledb.connect(user=user, password=password, dsn=dsn)
        print("✅ Conexão estabelecida.\n")
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        return

    cur = conn.cursor()

    # Tabela
    try:
        cur.execute(DDL_TABELA)
        conn.commit()
        print("✅ Tabela 'agrosafe_perdas' criada com sucesso.")
    except oracledb.DatabaseError as e:
        if "ORA-00955" in str(e):  # Tabela já existe
            print("ℹ  Tabela 'agrosafe_perdas' já existia — pulando criação.")
        else:
            print(f"❌ Erro ao criar tabela: {e}")

    # Index
    try:
        cur.execute(DDL_INDEX)
        conn.commit()
        print("✅ Índice criado com sucesso.")
    except oracledb.DatabaseError as e:
        if "ORA-01408" in str(e) or "ORA-00955" in str(e):
            print("ℹ  Índice já existia — pulando criação.")
        else:
            print(f"❌ Erro ao criar índice: {e}")

    conn.close()
    print("\n✅ Setup concluído!")

if __name__ == "__main__":
    setup()
