# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href="https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP" width="200"/></a>
</p>

---

# AgroSafe — Sistema de Monitoramento de Perdas na Colheita

## Grupo AgroSafe

## 👨‍🎓 Integrantes

- Kauan Maciel Forgiarini
- Wagner Adriano De Souza Silva Junior
- Thiago Lucas da Costa Bessa
- Beatriz de Oliveira Ossola Ribeiro
- Willian Kauê Tobias do Carmo 

## 👩‍🏫 Professores

### Tutor(a)
- André Godoi Chiovanto

### Coordenador(a)
- Sabrina Otoni

---

## 📜 Descrição

### 🌾 Problema do Agronegócio

O Brasil é o maior produtor e exportador de soja do mundo, respondendo por aproximadamente 37% da produção global. No entanto, segundo a **EMBRAPA Soja**, perdas durante a colheita chegam a **80 kg por hectare** em situações críticas, quando o aceitável é abaixo de 60 kg/ha. Em uma safra de 45 milhões de hectares cultivados, isso representa bilhões de reais em grãos deixados no campo.

As causas mais comuns são:
- Regulagem inadequada da colhedora
- Colheita em horário ou umidade incorretos
- Falta de monitoramento sistemático das perdas por talhão/fazenda
- Ausência de histórico para comparação entre safras

### 💡 Solução Proposta: AgroSafe

O **AgroSafe** é um sistema de terminal em Python que permite ao produtor rural e ao técnico agrícola **registrar, monitorar e analisar perdas na colheita** de forma sistemática, gerando indicadores e recomendações baseadas nos padrões da EMBRAPA.

O sistema permite:

1. **Registrar ocorrências** de perda por fazenda, cultura, fase e área colhida
2. **Calcular automaticamente** a perda em kg/ha, o percentual de perda e o prejuízo financeiro estimado
3. **Classificar** a severidade da perda em 4 níveis (Excelente / Aceitável / Atenção / Crítica)
4. **Gerar recomendações** técnicas personalizadas por fase da colheita e cultura
5. **Exibir relatório consolidado** com estatísticas de toda a operação
6. **Buscar histórico** por fazenda para comparação entre safras
7. **Simular cenários** hipotéticos sem persistência de dados

### 🎯 Impacto

Com o AgroSafe, produtores e técnicos deixam de operar "no escuro" e passam a ter dados estruturados para decisões de regulagem, planejamento de colheita e negociação com seguradoras.

---

## 📁 Estrutura de Pastas

```
agro_projeto/
│
├── .github/           # Configurações do GitHub Actions (CI)
├── assets/            # Imagens e recursos estáticos (logo FIAP)
│
├── config/
│   └── db_config.py   # Parâmetros de conexão Oracle e configurações gerais
│
├── document/
│   └── other/         # Documentos complementares
│
├── scripts/
│   ├── setup_oracle.py  # DDL: criação da tabela no Oracle
│   ├── carga_demo.py    # Popula dados fictícios para demonstração
│   └── testes.py        # Suite de testes automatizados
│
├── src/
│   └── colheita_monitor.py  # Código-fonte principal (entry point)
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🔧 Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- (Opcional) Oracle Database acessível com `oracledb`

### Passo 1 — Clonar o repositório

```bash
git clone https://github.com/seu-usuario/agro_projeto.git
cd agro_projeto
```

### Passo 2 — Instalar dependências

```bash
pip install -r requirements.txt
```

> **Nota:** Se não tiver acesso ao Oracle, o sistema funciona normalmente em modo offline (persistência via JSON e TXT).

### Passo 3 — (Opcional) Configurar o Oracle

```bash
export ORACLE_USER=rm12345
export ORACLE_PASSWORD=sua_senha
export ORACLE_DSN=oracle.fiap.com.br:1521/orcl

python scripts/setup_oracle.py
```

### Passo 4 — (Opcional) Carregar dados de demonstração

```bash
python scripts/carga_demo.py
```

### Passo 5 — Executar o sistema

```bash
cd src
python colheita_monitor.py
```

### Passo 6 — Executar testes

```bash
python scripts/testes.py
```

---

## 🗂️ Conteúdos Implementados

| Requisito | Onde |
|-----------|------|
| Funções e procedimentos com passagem de parâmetros | `calcular_perda_kg_ha()`, `classificar_perda()`, `gerar_recomendacoes()` etc. |
| Listas | `CULTURAS_VALIDAS`, `FASES_COLHEITA`, lista de recomendações |
| Tuplas | Retorno de `classificar_perda()` → `(classificação, emoji)` |
| Dicionários | Cada registro é um `dict`; `contagem` no relatório |
| Arquivos TXT | `salvar_txt()` / log em `registros_perdas.txt` |
| Arquivos JSON | `salvar_json()` / `carregar_json()` em `registros_perdas.json` |
| Banco Oracle | `obter_conexao_oracle()`, `inserir_oracle()`, `listar_oracle()` |
| Validação de entrada | `validar_float()`, `validar_inteiro()`, `validar_opcao()`, `validar_ano()` |

---

## 🗃 Histórico de Lançamentos

- **0.1.0** — 18/04/2025 — Versão inicial com CRUD local (TXT + JSON)
- **0.2.0** — 25/04/2025 — Integração Oracle e relatório consolidado
- **0.3.0** — 02/05/2025 — Simulador de cenários e buscas por fazenda
- **0.4.0** — 09/05/2025 — Recomendações técnicas por fase/cultura
- **0.5.0** — 16/05/2025 — Suite de testes e script de carga de demo

---

## 📋 Licença

[![CC BY 4.0](https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1)](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1)
[![BY](https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1)](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1)

[MODELO GIT FIAP](https://github.com/agodoi/templateFiapVfinal) por [FIAP](https://fiap.com.br) está licenciado sob [Attribution 4.0 International](http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1).
