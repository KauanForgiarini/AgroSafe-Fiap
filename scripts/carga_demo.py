"""
=============================================================
  AgroSafe — Carga de Dados de Demonstração
  Popula o JSON local com registros realistas para demo.
=============================================================
Execute: python scripts/carga_demo.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from colheita_monitor import (
    calcular_perda_kg_ha, calcular_perda_percentual,
    calcular_prejuizo_financeiro, classificar_perda, salvar_json
)
import json
from datetime import datetime, timedelta
import random

# Dados fictícios representando fazendas do Centro-Oeste brasileiro
FAZENDAS = [
    ("Fazenda São Marcos",    "soja",   "pré-colheita",  45, 3200, 0.013),
    ("Fazenda Bela Vista",    "soja",   "colheita",       90, 3500, 0.025),
    ("Fazenda Boa Esperança", "milho",  "colheita",       70, 8000, 0.021),
    ("Fazenda Santa Clara",   "soja",   "pós-colheita",  35, 3100, 0.010),
    ("Fazenda Rio Claro",     "soja",   "colheita",      120, 3400, 0.035),
    ("Fazenda Vitória",       "trigo",  "pré-colheita",  55, 4200, 0.015),
    ("Fazenda Cerradão",      "soja",   "colheita",      200, 3300, 0.055),
    ("Fazenda Nova Terra",    "soja",   "pós-colheita",  80, 3600, 0.018),
]

registros = []
data_base = datetime.now() - timedelta(days=60)

for i, (fazenda, cultura, fase, area, prod_kg_ha, perda_fator) in enumerate(FAZENDAS):
    data = data_base + timedelta(days=i * 7 + random.randint(0, 3))
    producao_total = area * prod_kg_ha
    perda_total    = producao_total * perda_fator
    perda_kg_ha    = calcular_perda_kg_ha(perda_total, area)
    perda_pct      = calcular_perda_percentual(perda_total, producao_total)
    prejuizo       = calcular_prejuizo_financeiro(perda_total, 145.0)
    classif, _     = classificar_perda(perda_kg_ha)

    registros.append({
        "data_hora"     : data.strftime("%Y-%m-%d %H:%M:%S"),
        "fazenda"       : fazenda,
        "cultura"       : cultura,
        "ano_safra"     : 2024,
        "fase_colheita" : fase,
        "area_ha"       : area,
        "producao_kg"   : round(producao_total),
        "perda_total_kg": round(perda_total),
        "perda_kg_ha"   : round(perda_kg_ha, 2),
        "perda_pct"     : round(perda_pct, 2),
        "preco_saca"    : 145.0,
        "prejuizo_rs"   : round(prejuizo, 2),
        "classificacao" : classif,
    })

# Salva no JSON
caminho = os.path.join(os.path.dirname(__file__), "..", "src", "registros_perdas.json")
with open(caminho, "w", encoding="utf-8") as f:
    json.dump(registros, f, ensure_ascii=False, indent=4)

print(f"✅ {len(registros)} registros de demonstração criados em: {caminho}")
