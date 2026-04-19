# =============================================================
#  AgroSafe — Configuração do Banco de Dados Oracle
#  Arquivo: config/db_config.py
#
#  ATENÇÃO: Não commite credenciais reais neste arquivo.
#  Use variáveis de ambiente em produção:
#    export ORACLE_USER=seu_rm
#    export ORACLE_PASSWORD=sua_senha
#    export ORACLE_DSN=oracle.fiap.com.br:1521/orcl
# =============================================================

import os

DB_CONFIG = {
    "user"    : os.getenv("ORACLE_USER",     "rm12345"),
    "password": os.getenv("ORACLE_PASSWORD", "senha123"),
    "dsn"     : os.getenv("ORACLE_DSN",      "oracle.fiap.com.br:1521/orcl"),
}

# Configurações da aplicação
APP_CONFIG = {
    "arquivo_txt"           : "registros_perdas.txt",
    "arquivo_json"          : "registros_perdas.json",
    "limite_perda_critica"  : 80.0,   # kg/ha — referência EMBRAPA
    "limite_perda_atencao"  : 60.0,
    "limite_perda_aceitavel": 40.0,
    "preco_saca_padrao"     : 145.0,  # R$/saca de 60 kg
}
