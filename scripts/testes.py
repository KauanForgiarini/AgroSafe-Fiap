"""
=============================================================
  AgroSafe — Testes automatizados das funções core
=============================================================
Execute: python scripts/testes.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from colheita_monitor import (
    calcular_perda_kg_ha,
    calcular_perda_percentual,
    calcular_prejuizo_financeiro,
    classificar_perda,
    gerar_recomendacoes,
)

PASS = "✅ PASS"
FAIL = "❌ FAIL"
erros = 0


def testar(descricao: str, resultado, esperado) -> None:
    global erros
    if resultado == esperado:
        print(f"  {PASS}  {descricao}")
    else:
        print(f"  {FAIL}  {descricao}")
        print(f"         Esperado : {esperado}")
        print(f"         Obtido   : {resultado}")
        erros += 1


print("=" * 55)
print("  AgroSafe — Suite de Testes")
print("=" * 55)

# --- calcular_perda_kg_ha ---
print("\n▶ calcular_perda_kg_ha")
testar("500 kg / 10 ha = 50 kg/ha",      calcular_perda_kg_ha(500, 10),  50.0)
testar("Divisão por zero retorna 0",      calcular_perda_kg_ha(100, 0),   0.0)
testar("1000 kg / 25 ha = 40 kg/ha",     calcular_perda_kg_ha(1000, 25), 40.0)

# --- calcular_perda_percentual ---
print("\n▶ calcular_perda_percentual")
testar("10% de 1000 kg = 10%",           calcular_perda_percentual(100, 1000),  10.0)
testar("Produção zero retorna 0",         calcular_perda_percentual(50, 0),      0.0)
testar("Perda zero = 0%",                 calcular_perda_percentual(0, 500),     0.0)

# --- calcular_prejuizo_financeiro ---
print("\n▶ calcular_prejuizo_financeiro")
testar("120 kg / 60 * R$150 = R$300",    calcular_prejuizo_financeiro(120, 150), 300.0)
testar("0 kg = R$0",                      calcular_prejuizo_financeiro(0, 200),     0.0)
testar("60 kg a R$120 = R$120",           calcular_prejuizo_financeiro(60, 120),  120.0)

# --- classificar_perda ---
print("\n▶ classificar_perda")
testar("20 kg/ha → Excelente",            classificar_perda(20),  ("Excelente", "🟢"))
testar("40 kg/ha → Excelente (limite)",   classificar_perda(40),  ("Excelente", "🟢"))
testar("55 kg/ha → Aceitável",            classificar_perda(55),  ("Aceitável", "🟡"))
testar("75 kg/ha → Atenção",              classificar_perda(75),  ("Atenção",   "🟠"))
testar("90 kg/ha → Crítica",              classificar_perda(90),  ("Crítica",   "🔴"))
testar("0 kg/ha → Excelente",             classificar_perda(0),   ("Excelente", "🟢"))

# --- gerar_recomendacoes ---
print("\n▶ gerar_recomendacoes")
rec_critica = gerar_recomendacoes({"perda_kg_ha": 100, "fase_colheita": "colheita", "cultura": "soja"})
testar("Perda crítica gera recomendações", len(rec_critica) > 0, True)

rec_ok = gerar_recomendacoes({"perda_kg_ha": 10, "fase_colheita": "colheita", "cultura": "milho"})
testar("Perda baixa ainda retorna recomendações operacionais", len(rec_ok) > 0, True)

rec_sem_fase = gerar_recomendacoes({"perda_kg_ha": 5, "fase_colheita": "pós-colheita", "cultura": "trigo"})
testar("Perda mínima em pós-colheita gera recomendação", len(rec_sem_fase) > 0, True)

# Resultado final
print()
print("=" * 55)
if erros == 0:
    print("  ✅ Todos os testes passaram!")
else:
    print(f"  ❌ {erros} teste(s) falharam.")
print("=" * 55)
