"""Valida os cenários gerados rodando a regressão real do backend."""
import sys
sys.path.insert(0, r"C:\Users\welli\OneDrive\Documentos\FAE\Expandir_Framework\backend")
from app.regression import rodar_regressao

ARQUIVOS = [
    ("ORIGINAL", r"C:\Users\welli\Downloads\Base Expandir_Final_Dados_Originais.xlsx"),
    ("BOM",      r"C:\Users\welli\OneDrive\Documentos\FAE\Expandir_Framework\bases\Base_PriceLab_Cenario_Bom.xlsx"),
    ("RUIM",     r"C:\Users\welli\OneDrive\Documentos\FAE\Expandir_Framework\bases\Base_PriceLab_Cenario_Ruim.xlsx"),
]

for nome, arq in ARQUIVOS:
    res = rodar_regressao(arq)
    print(f"--- {nome} ---")
    for sv in ("expansao", "formatacao", "validacao"):
        r = res[sv]
        print(f"  {sv:11s} margem={r['margem_observada']*100:+6.1f}%  "
              f"cpc=R${r['custo_por_contrato']:>10,.0f}  "
              f"preco6=R${r['preco_ideal_6']:>10,.0f}  R2={r['r2']:.3f}")
