"""
Regressão Linear OLS — Expandir Franquias (Base v4)
Disciplina: Data Analysis in Business Project

Estrutura do modelo:
  - Três regressões separadas (uma por tipo de serviço)
  - Modelo 1: Y = Total_Custos  → usado para calcular preço ideal
  - Modelo 2: Y = Margem_%      → usado para diagnosticar rentabilidade
  - Elasticidades calculadas no ponto da média para cada variável

Premissas incorporadas na base v4:
  - 176h úteis/mês
  - Consultor PJ R$12.500: 75% Formatação / 25% Validação
  - H_Advogado como driver de complexidade jurídica (Formatação)
  - CAC variável por tier (Formatação): R$5.098 / R$6.098 / R$7.098
  - Contabilidade R$2.774: 75% Formatação / 25% Validação (custo fixo rateado)
  - GP R$3.000 fixo rateado na Validação (não entra na regressão)
  - H_GP descartada da regressão (correlação não significativa com custos)
  - SDR zerado na Validação (não atua nessa fase)
"""

import pickle
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error


# ─────────────────────────────────────────────────────────────────────────────
# 1. CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────────────────────────────────────
# Carrega o pickle gerado pelo script de geração da base v4.
# Cada registro = 1 observação de Mês × Franquia × Tipo_Servico.
df_excel = pd.read_excel('Base_Expandir_v4.xlsx', sheet_name='4_Base_Regressao')
df_excel.to_pickle("registros_v4.pkl")

# 3. Lê o arquivo .pkl de volta para a variável 'registros'
# O read_pickle já retorna um objeto DataFrame pronto para uso
registros = pd.read_pickle("registros_v4.pkl")

df = pd.DataFrame(registros)
print(f"Base carregada: {len(df)} registros | Serviços: {df['Tipo_Servico'].unique()}")

print(df.columns)

# ─────────────────────────────────────────────────────────────────────────────
# 2. FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────────────────────────────────────
def agregar(df, servico):
    """
    Agrega os dados do serviço por Mês × Franquia.
    Cada linha da base bruta é um contrato; após a agregação,
    cada linha é um período mensal por franquia — a unidade
    correta para a regressão de série temporal.
    """
    sub = df[df["Tipo_Servico"] == servico].copy()
    g = sub.groupby(["Mês", "Franquia"]).agg(
        Receita_Total =("Receita_Total", "sum"),
        Qtd_Contratos =("Qtd_Contratos", "sum"),
        H_Total         =("H_Total",       "sum"),
        H_Advogado    =("H_Advogado",    "sum"),
        Total_Custos  =("Total_Custos",  "sum"),
        Margem_RS     =("Margem_RS",     "sum"),
    ).reset_index()

    g["Margem_PCT"] = g["Margem_RS"] / g["Receita_Total"]
    g["Num_Mes"]    = g["Mês"].str.split("-").str[1].astype(int)
    return g


def rodar_ols(agg, variaveis):
    """
    Ajusta dois modelos OLS:
      - m1: Y = Total_Custos (modelo de custo — base do preço ideal)
      - m2: Y = Margem_%     (modelo de rentabilidade — diagnóstico)

    A coluna de intercepto (β₀) é adicionada manualmente via np.ones,
    garantindo consistência na extração dos coeficientes.
    """
    X_raw = agg[variaveis].astype(float).values
    X     = np.column_stack([np.ones(len(X_raw)), X_raw])
    y1    = agg["Total_Custos"].astype(float).values
    y2    = agg["Margem_PCT"].astype(float).values
    m1    = sm.OLS(y1, X).fit()
    m2    = sm.OLS(y2, X).fit()
    return m1, m2, y1, y2


def elasticidades(modelo, agg, variaveis):
    """
    Calcula a elasticidade pontual de cada variável X no ponto da média:

        ε_xi = β_i × (X̄_i / Ȳ)

    Interpretação prática:
        Um aumento de 1% em X_i provoca uma variação de ε_xi%
        no Custo_Total, mantendo todas as outras variáveis constantes,
        avaliado na média dos dados do período.

    Exemplo: ε_Qtd_Contratos = +0.23 significa que fechar 1% mais
    contratos eleva o custo em 0.23% — custo relativamente inelástico
    ao volume neste serviço.
    """
    names  = ["const"] + variaveis
    y_mean = agg["Total_Custos"].mean()
    elast  = {}
    for i, nm in enumerate(names):
        if nm == "const":
            continue
        x_mean    = agg[nm].mean()
        beta      = modelo.params[i]
        elast[nm] = beta * (x_mean / y_mean)
    return elast


def preco_ideal(modelo, agg, margem_alvo=0.30):
    """
    Calcula o preço por contrato necessário para atingir a margem alvo:

        Preço_ideal = Custo_previsto_por_contrato ÷ (1 − Margem_alvo)

    Essa é a prova real do modelo: dado que o modelo prevê um custo,
    qual deve ser o preço para garantir a margem desejada?
    """
    custo_total_previsto = modelo.fittedvalues.mean()
    qtd_media            = agg["Qtd_Contratos"].mean()
    custo_por_contrato   = custo_total_previsto / qtd_media
    return custo_por_contrato / (1 - margem_alvo), custo_por_contrato


def imprimir_resultados(servico, m1, m2, y1, y2, agg, variaveis, elast, cpc, p_ideal):
    names = ["const"] + variaveis
    sig   = lambda p: "***" if p<0.01 else ("**" if p<0.05 else ("*" if p<0.1 else "ns"))
    mae1  = mean_absolute_error(y1, m1.fittedvalues)
    rmse1 = np.sqrt(mean_squared_error(y1, m1.fittedvalues))

    print(f"\n{'='*62}")
    print(f"  {servico.upper()}  (n={len(agg)} observações — Mês × Franquia)")
    print(f"{'='*62}")

    print(f"\n  ── MODELO 1 — Y = Total_Custos ──────────────────────────")
    print(f"  R²         : {m1.rsquared:.4f}")
    print(f"  R² ajust.  : {m1.rsquared_adj:.4f}")
    print(f"  F-stat     : {m1.fvalue:.2f}  (p={m1.f_pvalue:.5f})")
    print(f"  MAE        : R$ {mae1:,.0f}")
    print(f"  RMSE       : R$ {rmse1:,.0f}")
    print(f"\n  Coeficientes:")
    for nm, c, p in zip(names, m1.params, m1.pvalues):
        print(f"    {nm:24s}: {c:>10,.2f}  (p={p:.3f})  {sig(p)}")

    print(f"\n  Elasticidades — ponto na média  [ε = β × (X̄ / Ȳ)]:")
    for nm, e in elast.items():
        barra = "█" * int(abs(e) * 30)
        sinal = "+" if e >= 0 else "-"
        print(f"    ε_{nm:22s}: {e:>+.4f}  {barra}")
    print(f"\n  Equação estimada:")
    termos = [f"  {m1.params[0]:,.2f}"]
    for nm, c in zip(variaveis, m1.params[1:]):
        sinal = "+" if c >= 0 else "-"
        termos.append(f"  {sinal} {abs(c):,.2f} × {nm}")
    print(f"  Custo = " + "\n         ".join(termos))

    print(f"\n  ── MODELO 2 — Y = Margem_% ──────────────────────────────")
    print(f"  R²         : {m2.rsquared:.4f}")
    print(f"  Margem obs.: {agg['Margem_PCT'].mean():>+.1%}")
    mae2 = mean_absolute_error(y2, m2.fittedvalues)
    print(f"  MAE        : {mae2:.4f} ({mae2*100:.2f} p.p.)")

    print(f"\n  ── PRECIFICAÇÃO ─────────────────────────────────────────")
    print(f"  Custo médio/contrato : R$ {cpc:,.0f}")
    print(f"  Preço de breakeven   : R$ {cpc:,.0f}  (margem 0%)")
    print(f"  Preço ideal (30%)    : R$ {p_ideal:,.0f}")
    print(f"  Preço ideal (20%)    : R$ {cpc/0.80:,.0f}")
    print(f"  Preço ideal (40%)    : R$ {cpc/0.60:,.0f}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. EXPANSÃO
#
# Variáveis do modelo:
#   Qtd_Contratos — volume de contratos fechados no período
#   H_Total       — horas SDR + horas consultor (residual ~10% do pool)
#   Num_Mes       — tendência temporal (1 a 12)
#
# Observação: R² baixo (~0.10) indica que o mix de tier de preço
# é o principal driver de margem, não o volume ou as horas.
# A regressão captura a estrutura de custo variável, mas não o
# efeito do preço — que deveria ser modelado com dummies de tier.
# ─────────────────────────────────────────────────────────────────────────────

agg_exp  = agregar(df, "Expansão")
vars_exp = ["Qtd_Contratos", "H_Total", "Num_Mes"]
m1_exp, m2_exp, y1_exp, y2_exp = rodar_ols(agg_exp, vars_exp)
elast_exp = elasticidades(m1_exp, agg_exp, vars_exp)
p_ideal_exp, cpc_exp = preco_ideal(m1_exp, agg_exp)
imprimir_resultados("Expansão", m1_exp, m2_exp, y1_exp, y2_exp,
                    agg_exp, vars_exp, elast_exp, cpc_exp, p_ideal_exp)



# ─────────────────────────────────────────────────────────────────────────────
# 4. FORMATAÇÃO
#
# Variáveis do modelo:
#   Qtd_Contratos — volume de contratos fechados
#   H_Total       — horas SDR + consultor (pool: 75% das 176h = 132h)
#   H_Advogado    — driver de complexidade jurídica (8 a 35h/contrato)
#   Num_Mes       — tendência temporal
#
# H_Advogado é a variável nova da v4. R² salta de ~0.12 para ~0.95
# com sua inclusão — ela é o principal driver de variação de custo.
# CAC variável e contabilidade já embutidos no Total_Custos (fixo rateado).
# ─────────────────────────────────────────────────────────────────────────────

agg_fmt  = agregar(df, "Formatação")
vars_fmt = ["Qtd_Contratos", "H_Total", "H_Advogado", "Num_Mes"]
m1_fmt, m2_fmt, y1_fmt, y2_fmt = rodar_ols(agg_fmt, vars_fmt)
elast_fmt = elasticidades(m1_fmt, agg_fmt, vars_fmt)
p_ideal_fmt, cpc_fmt = preco_ideal(m1_fmt, agg_fmt)
imprimir_resultados("Formatação", m1_fmt, m2_fmt, y1_fmt, y2_fmt,
                    agg_fmt, vars_fmt, elast_fmt, cpc_fmt, p_ideal_fmt)


# ─────────────────────────────────────────────────────────────────────────────
# 5. VALIDAÇÃO
#
# Variáveis do modelo:
#   Qtd_Contratos — volume de contratos
#   H_Total       — apenas H_Consultor (SDR = 0 nessa fase)
#   Num_Mes       — tendência temporal
#
# Variáveis excluídas e motivo:
#   H_SDR  → zerado na Validação (não atua nessa fase)
#   H_GP   → descartada (correlação não significativa; custo é fixo)
#
# Custos fixos rateados (não entram na regressão, mas compõem Total_Custos):
#   GP R$3.000/mês ÷ contratos do período
#   Contabilidade R$694/mês (25% de R$2.774) ÷ contratos do período
#
# R² baixo (~0.21 no M1) porque GP e contabilidade são fixos —
# há pouca variação de custo para a regressão explicar.
# M2 (Margem_%) tem R² alto (~0.95) pois a margem varia mais.
# ─────────────────────────────────────────────────────────────────────────────

agg_val = agregar(df, "Validação")
agg_val["H_Total"] = agg_val["H_Total"]  # SDR zerado nessa fase
vars_val = ["Qtd_Contratos", "H_Total", "Num_Mes"]
m1_val, m2_val, y1_val, y2_val = rodar_ols(agg_val, vars_val)
elast_val = elasticidades(m1_val, agg_val, vars_val)
p_ideal_val, cpc_val = preco_ideal(m1_val, agg_val)
imprimir_resultados("Validação", m1_val, m2_val, y1_val, y2_val,
                    agg_val, vars_val, elast_val, cpc_val, p_ideal_val)


# ─────────────────────────────────────────────────────────────────────────────
# 6. SIMULAÇÃO — PROJEÇÃO PARA NOVOS CENÁRIOS (mês 13)
#
# Aplica a equação aprendida para estimar o custo e o preço ideal
# dado qualquer combinação de inputs planejados pela empresa.
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n\n{'='*62}")
print("  SIMULAÇÃO — Custo e preço ideal para o mês 13")
print(f"{'='*62}")

def simular(modelo, variaveis, inputs, margem_alvo=0.30):
    """
    Projeta custo total e preço ideal para um cenário customizado.
    inputs: dict com os valores de cada variável (sem o intercepto).
    """
    x_vec = [1.0] + [inputs[v] for v in variaveis]
    custo  = sum(b*x for b,x in zip(modelo.params, x_vec))
    qtd    = inputs["Qtd_Contratos"]
    cpc    = custo / qtd
    return custo, cpc, cpc / (1 - margem_alvo)

cenarios = [
    ("Expansão",   m1_exp, vars_exp, {"Qtd_Contratos":4, "H_Total":280, "Num_Mes":13}),
    ("Expansão",   m1_exp, vars_exp, {"Qtd_Contratos":8, "H_Total":560, "Num_Mes":13}),
    ("Formatação", m1_fmt, vars_fmt, {"Qtd_Contratos":1, "H_Total":150, "H_Advogado":12, "Num_Mes":13}),
    ("Formatação", m1_fmt, vars_fmt, {"Qtd_Contratos":3, "H_Total":450, "H_Advogado":30, "Num_Mes":13}),
    ("Validação",  m1_val, vars_val, {"Qtd_Contratos":1, "H_Total":31,  "Num_Mes":13}),
    ("Validação",  m1_val, vars_val, {"Qtd_Contratos":2, "H_Total":62,  "Num_Mes":13}),
]

for sv, modelo, variaveis, inp in cenarios:
    ct, cpc, pi = simular(modelo, variaveis, inp)
    desc = " | ".join(f"{k}={v}" for k,v in inp.items() if k != "Num_Mes")
    print(f"  {sv:12s} | {desc}")
    print(f"              Custo total: R${ct:,.0f}  |  Custo/ct: R${cpc:,.0f}  |  Preço ideal 30%: R${pi:,.0f}\n")


# ─────────────────────────────────────────────────────────────────────────────
# 7. COMO USAR COM DADOS REAIS
#
# 1. Substitua o arquivo registros_v4.pkl pela base real em formato pickle,
#    ou adapte o carregamento para ler diretamente de um CSV ou banco SQLite.
# 2. Garanta que as colunas tenham os mesmos nomes usados aqui.
# 3. Execute o script — os coeficientes se recalibram automaticamente.
# 4. Os valores de β e elasticidade impressos são os que devem ser
#    inseridos no dashboard HTML (seção "Configurar Coeficientes").
# ─────────────────────────────────────────────────────────────────────────────
