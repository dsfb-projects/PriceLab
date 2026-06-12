"""
Auditoria valor-a-valor: roda a MESMA lógica do código final do Léo
contra a base real e imprime tudo que a tela do PriceLab exibe (ou deveria exibir).

Uso:  python auditoria_valores.py
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error

sys.path.insert(0, r"C:\Users\welli\OneDrive\Documentos\FAE\Expandir_Framework\backend")
from app.regression import agregar, rodar_ols, elasticidades, preco_ideal, carregar_df

BASE = r"C:\Users\welli\Downloads\Base Expandir_Final.xlsx"

df, aba = carregar_df(BASE)
print(f"Base: {len(df)} registros | aba '{aba}' | servicos: {df['Tipo_Servico'].unique().tolist()}\n")

SERVICOS = {
    "Expansão":   ["Qtd_Contratos", "H_Total", "Num_Mes"],
    "Formatação": ["Qtd_Contratos", "H_Total", "H_Advogado", "Num_Mes"],
    "Validação":  ["Qtd_Contratos", "H_Total", "Num_Mes"],
}

sig = lambda p: "***" if p < 0.01 else ("**" if p < 0.05 else ("*" if p < 0.1 else "ns"))

for servico, variaveis in SERVICOS.items():
    agg = agregar(df, servico)
    m1, m2, y1, y2 = rodar_ols(agg, variaveis)
    elast = elasticidades(m1, agg, variaveis)
    p6, cpc = preco_ideal(m1, agg)
    sub = df[df["Tipo_Servico"] == servico]
    margem_raw = float((sub["Margem_RS"] / sub["Receita_Total"]).mean())

    names = ["const"] + variaveis
    print("=" * 64)
    print(f"  {servico.upper()}  (n={len(agg)})")
    print("=" * 64)
    print(f"  M1  R²={m1.rsquared:.4f}  R²adj={m1.rsquared_adj:.4f}  "
          f"F={m1.fvalue:.2f} (p={m1.f_pvalue:.5f})")
    print(f"  M1  MAE=R${mean_absolute_error(y1, m1.fittedvalues):,.0f}  "
          f"RMSE=R${np.sqrt(mean_squared_error(y1, m1.fittedvalues)):,.0f}")
    print(f"  Coeficientes M1:")
    for nm, c, p in zip(names, m1.params, m1.pvalues):
        print(f"    {nm:16s}: {c:>12,.2f}  (p={p:.3f}) {sig(p)}")
    print(f"  Elasticidades: " + "  ".join(f"{k}={v:+.4f}" for k, v in elast.items()))
    mae2 = mean_absolute_error(y2, m2.fittedvalues)
    print(f"  M2  R²={m2.rsquared:.4f}  MAE={mae2*100:.2f} p.p.")
    print(f"  Margem obs. (agg) = {agg['Margem_PCT'].mean():+.1%}   "
          f"Margem obs. (raw) = {margem_raw:+.1%}")
    print(f"  Custo/contrato = R${cpc:,.2f}")
    print(f"  Preço ideal  6% = R${p6:,.2f}   10% = R${cpc/0.90:,.2f}   15% = R${cpc/0.85:,.2f}")
    print()
