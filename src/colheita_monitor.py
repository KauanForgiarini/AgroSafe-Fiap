"""
=============================================================
  AgroSafe - Sistema de Monitoramento de Perdas na Colheita
  FIAP - Curso de Inteligência Artificial
  Problema: Perdas na colheita de soja no Brasil
=============================================================
"""

import json
import os
from datetime import datetime
from typing import Optional

# ─── Importação do banco de dados Oracle ─────────────────────
try:
    import oracledb
    ORACLE_DISPONIVEL = True
except ImportError:
    ORACLE_DISPONIVEL = False

# ─── Constantes do domínio ───────────────────────────────────
CULTURAS_VALIDAS = ("soja", "milho", "trigo", "algodão", "arroz", "feijão")
FASES_COLHEITA = ("pré-colheita", "colheita", "pós-colheita")
LIMITE_PERDA_CRITICA = 80.0   # kg/ha — referência EMBRAPA
ARQUIVO_LOG_TXT  = "registros_perdas.txt"
ARQUIVO_LOG_JSON = "registros_perdas.json"


# ══════════════════════════════════════════════════════════════
#  FUNÇÕES AUXILIARES — validação e formatação
# ══════════════════════════════════════════════════════════════

def limpar_tela() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def cabecalho(titulo: str) -> None:
    largura = 60
    print("=" * largura)
    print(f"  {titulo}".center(largura))
    print("=" * largura)


def validar_float(texto: str, minimo: float = 0.0, maximo: float = 1_000_000.0) -> float:
    """Lê e valida um número decimal dentro de um intervalo."""
    while True:
        try:
            valor = float(input(texto).replace(",", "."))
            if minimo <= valor <= maximo:
                return valor
            print(f"  ⚠  Informe um valor entre {minimo} e {maximo}.")
        except ValueError:
            print("  ⚠  Entrada inválida. Use apenas números.")


def validar_inteiro(texto: str, minimo: int = 1, maximo: int = 9_999) -> int:
    """Lê e valida um número inteiro dentro de um intervalo."""
    while True:
        try:
            valor = int(input(texto))
            if minimo <= valor <= maximo:
                return valor
            print(f"  ⚠  Informe um valor entre {minimo} e {maximo}.")
        except ValueError:
            print("  ⚠  Entrada inválida. Use apenas números inteiros.")


def validar_opcao(texto: str, opcoes: tuple) -> str:
    """Lê e valida uma escolha dentro de um conjunto fixo de opções."""
    lista = ", ".join(opcoes)
    while True:
        entrada = input(f"{texto} [{lista}]: ").strip().lower()
        if entrada in opcoes:
            return entrada
        print(f"  ⚠  Escolha uma das opções: {lista}")


def validar_ano(texto: str) -> int:
    ano_atual = datetime.now().year
    return validar_inteiro(texto, minimo=2000, maximo=ano_atual)


# ══════════════════════════════════════════════════════════════
#  CÁLCULO DE PERDAS
# ══════════════════════════════════════════════════════════════

def calcular_perda_kg_ha(perda_total_kg: float, area_ha: float) -> float:
    """Calcula perda em kg por hectare."""
    if area_ha <= 0:
        return 0.0
    return perda_total_kg / area_ha


def calcular_perda_percentual(perda_total_kg: float, producao_total_kg: float) -> float:
    """Calcula percentual de perda sobre a produção total."""
    if producao_total_kg <= 0:
        return 0.0
    return (perda_total_kg / producao_total_kg) * 100


def calcular_prejuizo_financeiro(perda_kg: float, preco_saca_60kg: float) -> float:
    """Converte perda em kg para prejuízo em R$."""
    sacas_perdidas = perda_kg / 60.0
    return sacas_perdidas * preco_saca_60kg


def classificar_perda(perda_kg_ha: float) -> tuple:
    """
    Retorna (classificação: str, emoji: str) com base na EMBRAPA.
    Referência: perdas aceitáveis < 60 kg/ha para soja.
    """
    if perda_kg_ha <= 40:
        return ("Excelente", "🟢")
    elif perda_kg_ha <= 60:
        return ("Aceitável", "🟡")
    elif perda_kg_ha <= LIMITE_PERDA_CRITICA:
        return ("Atenção", "🟠")
    else:
        return ("Crítica", "🔴")


def gerar_recomendacoes(registro: dict) -> list:
    """Gera lista de recomendações com base nos dados do registro."""
    recomendacoes = []
    perda = registro["perda_kg_ha"]
    fase  = registro["fase_colheita"]
    cultura = registro["cultura"]

    if perda > LIMITE_PERDA_CRITICA:
        recomendacoes.append("🔧 Revisar regulagem da colhedora imediatamente.")
        recomendacoes.append("📋 Auditar o processo de colheita com técnico especializado.")

    if fase == "pré-colheita":
        recomendacoes.append("🌡  Monitorar umidade do grão antes da colheita (ideal: 13-14%).")
        recomendacoes.append("📅 Planejar data de colheita para evitar excesso de maturação.")

    if fase == "colheita":
        recomendacoes.append("⚙️  Ajustar velocidade da colhedora conforme densidade da lavoura.")
        recomendacoes.append("🌬  Calibrar ventilação e peneiras conforme condição do grão.")

    if fase == "pós-colheita":
        recomendacoes.append("🏭 Verificar sistema de armazenagem e controle de umidade.")
        recomendacoes.append("🐛 Realizar manejo preventivo de pragas no armazém.")

    if cultura == "soja" and perda > 40:
    	recomendacoes.append("📐 Verificar altura da barra de corte (máx. 5-6 cm do solo).")

    if not recomendacoes:
        recomendacoes.append("✅ Operação dentro dos padrões recomendados. Mantenha o monitoramento!")

    return recomendacoes


# ══════════════════════════════════════════════════════════════
#  MANIPULAÇÃO DE ARQUIVOS
# ══════════════════════════════════════════════════════════════

def salvar_txt(registro: dict) -> None:
    """Acrescenta o registro no arquivo de log em texto simples."""
    with open(ARQUIVO_LOG_TXT, "a", encoding="utf-8") as f:
        linha = (
            f"[{registro['data_hora']}] "
            f"Fazenda: {registro['fazenda']} | "
            f"Cultura: {registro['cultura']} | "
            f"Fase: {registro['fase_colheita']} | "
            f"Área: {registro['area_ha']} ha | "
            f"Perda: {registro['perda_kg_ha']:.1f} kg/ha | "
            f"Classificação: {registro['classificacao']} | "
            f"Prejuízo: R$ {registro['prejuizo_rs']:.2f}\n"
        )
        f.write(linha)


def salvar_json(registro: dict) -> None:
    """Salva ou atualiza o arquivo JSON com todos os registros."""
    registros = carregar_json()
    registros.append(registro)
    with open(ARQUIVO_LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=4)


def carregar_json() -> list:
    """Carrega lista de registros do arquivo JSON. Retorna [] se não existir."""
    if not os.path.exists(ARQUIVO_LOG_JSON):
        return []
    try:
        with open(ARQUIVO_LOG_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


# ══════════════════════════════════════════════════════════════
#  BANCO DE DADOS ORACLE
# ══════════════════════════════════════════════════════════════

def obter_conexao_oracle() -> Optional[object]:
    """Retorna conexão Oracle ou None se não disponível."""
    if not ORACLE_DISPONIVEL:
        return None
    try:
        conn = oracledb.connect(
            user=os.getenv("ORACLE_USER", "rm12345"),
            password=os.getenv("ORACLE_PASSWORD", "senha123"),
            dsn=os.getenv("ORACLE_DSN", "oracle.fiap.com.br:1521/orcl"),
            mode=oracledb.SYSDBA if False else oracledb.DEFAULT_AUTH
        )
        return conn
    except Exception as e:
        print(f"  ⚠  Oracle indisponível: {e}")
        return None


def criar_tabela_oracle(conn) -> None:
    """Cria tabela de perdas no Oracle se não existir."""
    sql = """
        CREATE TABLE agrosafe_perdas (
            id          NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            data_hora   VARCHAR2(30),
            fazenda     VARCHAR2(100),
            cultura     VARCHAR2(50),
            fase        VARCHAR2(30),
            area_ha     NUMBER(10,2),
            perda_kg_ha NUMBER(10,2),
            prejuizo_rs NUMBER(15,2),
            classificacao VARCHAR2(20)
        )
    """
    try:
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    except Exception:
        pass  # Tabela já existe


def inserir_oracle(conn, registro: dict) -> bool:
    """Insere registro na tabela Oracle. Retorna True se sucesso."""
    sql = """
        INSERT INTO agrosafe_perdas
            (data_hora, fazenda, cultura, fase, area_ha, perda_kg_ha, prejuizo_rs, classificacao)
        VALUES
            (:1, :2, :3, :4, :5, :6, :7, :8)
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            registro["data_hora"],
            registro["fazenda"],
            registro["cultura"],
            registro["fase_colheita"],
            registro["area_ha"],
            registro["perda_kg_ha"],
            registro["prejuizo_rs"],
            registro["classificacao"],
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"  ⚠  Erro ao salvar no Oracle: {e}")
        return False


def listar_oracle(conn) -> list:
    """Retorna todos os registros da tabela Oracle."""
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT data_hora, fazenda, cultura, fase, area_ha, perda_kg_ha, "
            "prejuizo_rs, classificacao FROM agrosafe_perdas ORDER BY id DESC"
        )
        colunas = [d[0].lower() for d in cur.description]
        return [dict(zip(colunas, row)) for row in cur.fetchall()]
    except Exception as e:
        print(f"  ⚠  Erro ao consultar Oracle: {e}")
        return []


# ══════════════════════════════════════════════════════════════
#  FUNCIONALIDADES DO MENU
# ══════════════════════════════════════════════════════════════

def registrar_ocorrencia(conn) -> None:
    """Coleta dados do usuário, calcula métricas e persiste o registro."""
    cabecalho("REGISTRAR OCORRÊNCIA DE PERDA")

    fazenda = input("  Nome da fazenda: ").strip()
    if not fazenda:
        print("  ⚠  Nome da fazenda não pode ser vazio.")
        return

    cultura = validar_opcao("  Cultura", CULTURAS_VALIDAS)
    ano_safra = validar_ano("  Ano da safra: ")
    fase = validar_opcao("  Fase da colheita", FASES_COLHEITA)

    print("\n  --- Dados de Produção e Perda ---")
    area_ha          = validar_float("  Área colhida (ha): ", 0.1, 500_000)
    producao_total   = validar_float("  Produção total estimada (kg): ", 1)
    perda_total_kg   = validar_float("  Perda total estimada (kg): ", 0, producao_total)
    preco_saca       = validar_float("  Preço da saca (60 kg) em R$: ", 1, 10_000)

    # Cálculos
    perda_kg_ha   = calcular_perda_kg_ha(perda_total_kg, area_ha)
    perda_pct     = calcular_perda_percentual(perda_total_kg, producao_total)
    prejuizo      = calcular_prejuizo_financeiro(perda_total_kg, preco_saca)
    classif, emoji = classificar_perda(perda_kg_ha)
    recomendacoes = gerar_recomendacoes({
        "perda_kg_ha": perda_kg_ha,
        "fase_colheita": fase,
        "cultura": cultura
    })

    registro = {
        "data_hora"    : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fazenda"      : fazenda,
        "cultura"      : cultura,
        "ano_safra"    : ano_safra,
        "fase_colheita": fase,
        "area_ha"      : area_ha,
        "producao_kg"  : producao_total,
        "perda_total_kg": perda_total_kg,
        "perda_kg_ha"  : round(perda_kg_ha, 2),
        "perda_pct"    : round(perda_pct, 2),
        "preco_saca"   : preco_saca,
        "prejuizo_rs"  : round(prejuizo, 2),
        "classificacao": classif,
    }

    # Persistência
    salvar_txt(registro)
    salvar_json(registro)
    if conn:
        inserir_oracle(conn, registro)

    # Exibição do resultado
    print()
    cabecalho("RESULTADO DA ANÁLISE")
    print(f"  Fazenda       : {fazenda}")
    print(f"  Cultura       : {cultura.upper()}  |  Safra: {ano_safra}")
    print(f"  Fase          : {fase}")
    print(f"  Área colhida  : {area_ha:,.1f} ha")
    print(f"  Perda total   : {perda_total_kg:,.0f} kg  ({perda_pct:.1f}%)")
    print(f"  Perda/hectare : {perda_kg_ha:.1f} kg/ha")
    print(f"  Classificação : {emoji}  {classif}")
    print(f"  Prejuízo est. : R$ {prejuizo:,.2f}")
    print()
    print("  Recomendações:")
    for rec in recomendacoes:
        print(f"    {rec}")
    print()
    input("  Pressione ENTER para continuar...")


def listar_historico() -> None:
    """Exibe todos os registros salvos no JSON."""
    cabecalho("HISTÓRICO DE OCORRÊNCIAS")
    registros = carregar_json()

    if not registros:
        print("  Nenhum registro encontrado.")
        input("\n  Pressione ENTER para continuar...")
        return

    for i, r in enumerate(registros, 1):
        _, emoji = classificar_perda(r.get("perda_kg_ha", 0))
        print(f"\n  [{i}] {r['data_hora']}  —  {r['fazenda']}")
        print(f"       Cultura : {r['cultura']} | Fase: {r['fase_colheita']}")
        print(f"       Perda   : {r['perda_kg_ha']:.1f} kg/ha  {emoji} {r['classificacao']}")
        print(f"       Prejuízo: R$ {r['prejuizo_rs']:,.2f}")

    print()
    input("  Pressione ENTER para continuar...")


def relatorio_resumo() -> None:
    """Gera estatísticas consolidadas de todos os registros."""
    cabecalho("RELATÓRIO CONSOLIDADO")
    registros = carregar_json()

    if not registros:
        print("  Nenhum dado para gerar relatório.")
        input("\n  Pressione ENTER para continuar...")
        return

    total = len(registros)
    perdas = [r["perda_kg_ha"] for r in registros]
    prejuizos = [r["prejuizo_rs"] for r in registros]
    areas = [r["area_ha"] for r in registros]

    media_perda = sum(perdas) / total
    max_perda   = max(perdas)
    min_perda   = min(perdas)
    total_prej  = sum(prejuizos)
    total_area  = sum(areas)

    # Contagem por classificação
    contagem = {"Excelente": 0, "Aceitável": 0, "Atenção": 0, "Crítica": 0}
    for r in registros:
        contagem[r["classificacao"]] = contagem.get(r["classificacao"], 0) + 1

    print(f"  Total de registros   : {total}")
    print(f"  Área total monitorada: {total_area:,.1f} ha")
    print()
    print("  ── Perdas (kg/ha) ──────────────────────")
    print(f"  Média   : {media_perda:.1f}")
    print(f"  Máxima  : {max_perda:.1f}")
    print(f"  Mínima  : {min_perda:.1f}")
    print()
    print("  ── Prejuízo Total ──────────────────────")
    print(f"  R$ {total_prej:,.2f}")
    print()
    print("  ── Distribuição por Classificação ──────")
    for classif, qtd in contagem.items():
        _, emoji = classificar_perda(
            {"Excelente": 20, "Aceitável": 50, "Atenção": 70, "Crítica": 100}[classif]
        )
        pct = (qtd / total) * 100
        barra = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  {emoji} {classif:<12}: {barra} {qtd} ({pct:.0f}%)")

    print()
    input("  Pressione ENTER para continuar...")


def buscar_por_fazenda() -> None:
    """Filtra e exibe registros de uma fazenda específica."""
    cabecalho("BUSCAR POR FAZENDA")
    nome = input("  Nome da fazenda: ").strip().lower()
    registros = carregar_json()
    filtrados = [r for r in registros if nome in r["fazenda"].lower()]

    if not filtrados:
        print(f"  Nenhum registro encontrado para '{nome}'.")
    else:
        print(f"\n  Encontrados {len(filtrados)} registro(s):\n")
        for r in filtrados:
            _, emoji = classificar_perda(r["perda_kg_ha"])
            print(f"  • {r['data_hora']}  |  {r['fazenda']}  |  "
                  f"{r['perda_kg_ha']:.1f} kg/ha  {emoji}  R$ {r['prejuizo_rs']:,.2f}")

    print()
    input("  Pressione ENTER para continuar...")


def simular_cenario() -> None:
    """Simulador rápido sem salvar dados — permite análise hipotética."""
    cabecalho("SIMULADOR DE CENÁRIOS")
    print("  (Os dados desta simulação NÃO serão salvos)\n")

    area         = validar_float("  Área (ha): ", 0.1)
    producao     = validar_float("  Produção estimada (kg): ", 1)
    perda_pct    = validar_float("  Percentual de perda estimado (%): ", 0, 100)
    preco_saca   = validar_float("  Preço da saca (R$): ", 1)
    cultura      = validar_opcao("  Cultura", CULTURAS_VALIDAS)
    fase         = validar_opcao("  Fase", FASES_COLHEITA)

    perda_kg     = producao * (perda_pct / 100)
    perda_kg_ha  = calcular_perda_kg_ha(perda_kg, area)
    prejuizo     = calcular_prejuizo_financeiro(perda_kg, preco_saca)
    classif, emoji = classificar_perda(perda_kg_ha)
    recomendacoes = gerar_recomendacoes({
        "perda_kg_ha": perda_kg_ha,
        "fase_colheita": fase,
        "cultura": cultura
    })

    print()
    print(f"  Perda estimada  : {perda_kg:,.0f} kg  ({perda_pct:.1f}%)")
    print(f"  Perda/hectare   : {perda_kg_ha:.1f} kg/ha")
    print(f"  Classificação   : {emoji}  {classif}")
    print(f"  Prejuízo est.   : R$ {prejuizo:,.2f}")
    print()
    print("  Recomendações:")
    for rec in recomendacoes:
        print(f"    {rec}")

    print()
    input("  Pressione ENTER para continuar...")


# ══════════════════════════════════════════════════════════════
#  MENU PRINCIPAL
# ══════════════════════════════════════════════════════════════

def menu_principal(conn) -> None:
    while True:
        limpar_tela()
        cabecalho("AgroSafe — Monitoramento de Perdas na Colheita")
        status_db = "🟢 Oracle conectado" if conn else "⚪ Oracle offline (usando arquivos locais)"
        print(f"  {status_db}\n")
        print("  [1] Registrar ocorrência de perda")
        print("  [2] Listar histórico de ocorrências")
        print("  [3] Relatório consolidado")
        print("  [4] Buscar por fazenda")
        print("  [5] Simular cenário (sem salvar)")
        print("  [0] Sair")
        print()
        opcao = input("  Escolha uma opção: ").strip()

        if opcao == "1":
            registrar_ocorrencia(conn)
        elif opcao == "2":
            listar_historico()
        elif opcao == "3":
            relatorio_resumo()
        elif opcao == "4":
            buscar_por_fazenda()
        elif opcao == "5":
            simular_cenario()
        elif opcao == "0":
            print("\n  Encerrando AgroSafe. Boas colheitas! 🌾\n")
            break
        else:
            print("  ⚠  Opção inválida. Tente novamente.")
            input("  Pressione ENTER para continuar...")


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    limpar_tela()
    cabecalho("AgroSafe — Inicializando...")
    print()

    # Tenta conectar ao Oracle; continua mesmo sem conexão
    conn = obter_conexao_oracle()
    if conn:
        criar_tabela_oracle(conn)
        print("  ✅ Banco de dados Oracle conectado com sucesso.")
    else:
        print("  ℹ  Rodando em modo offline — dados salvos em arquivos locais.")

    print()
    input("  Pressione ENTER para acessar o sistema...")
    menu_principal(conn)

    if conn:
        conn.close()
