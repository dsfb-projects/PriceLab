"""
Módulo de regressão do backend Expandir.

O núcleo estatístico (agregar, rodar_ols, elasticidades, preco_ideal, simular)
é o código final do Léo (regressão - código final (Leo).py), copiado sem alteração de lógica.
Margem alvo padrão: 6% (conforme definição do negócio na versão final).

A única adição deste arquivo é a camada de carregamento flexível (carregar_df)
e o wrapper rodar_regressao() que converte os resultados para o formato JSON da API.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error


# ─────────────────────────────────────────────────────────────────────────────
# FUNÇÕES DO LÉO — copiadas de bases/regressão_v4_1.py sem alteração de lógica
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
        H_Total       =("H_Total",       "sum"),
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


def preco_ideal(modelo, agg, margem_alvo=0.06):
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


def simular(modelo, variaveis, inputs, margem_alvo=0.06):
    """
    Projeta custo total e preço ideal para um cenário customizado.
    inputs: dict com os valores de cada variável (sem o intercepto).
    """
    x_vec = [1.0] + [inputs[v] for v in variaveis]
    custo  = sum(b * x for b, x in zip(modelo.params, x_vec))
    qtd    = inputs["Qtd_Contratos"]
    cpc    = custo / qtd
    return custo, cpc, cpc / (1 - margem_alvo)


# ─────────────────────────────────────────────────────────────────────────────
# CARREGAMENTO FLEXÍVEL — wrapper da API
# ─────────────────────────────────────────────────────────────────────────────

# Nomes de aba aceitos, em ordem de prioridade
_SHEET_CANDIDATES = [
    "4_Base_Regressao",
    "Base_Regressao",
    "Regressao",
    "base_regressao",
    "Sheet1",
    "Planilha1",
]

# Colunas obrigatórias para rodar a regressão
_COLUNAS_OBRIGATORIAS = [
    "Mês", "Franquia", "Tipo_Servico",
    "Qtd_Contratos", "H_Total",
    "Total_Custos", "Receita_Total", "Margem_RS",
]

# Variações de nome de serviço aceitas (normalização)
_SERVICO_MAP = {
    "expansão": "Expansão", "expansao": "Expansão",
    "formatação": "Formatação", "formatacao": "Formatação",
    "validação": "Validação", "validacao": "Validação",
}


def carregar_df(caminho_excel):
    """
    Tenta carregar o DataFrame do Excel tentando múltiplos nomes de aba.
    Normaliza nomes de serviço e adiciona H_Advogado=0 se ausente.
    Levanta ValueError com mensagem clara se algo estiver errado.
    """
    # 1. Descobrir abas disponíveis
    try:
        abas = pd.ExcelFile(caminho_excel).sheet_names
    except Exception as e:
        raise ValueError(f"Não foi possível abrir o arquivo Excel: {e}")

    # 2. Tentar carregar em ordem de prioridade
    df = None
    aba_usada = None
    for candidato in _SHEET_CANDIDATES:
        if candidato in abas:
            df = pd.read_excel(caminho_excel, sheet_name=candidato)
            aba_usada = candidato
            break

    # 3. Se nenhuma aba conhecida, tenta a primeira aba disponível
    if df is None:
        df = pd.read_excel(caminho_excel, sheet_name=0)
        aba_usada = abas[0]

    # 4. Verificar colunas obrigatórias
    faltando = [c for c in _COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltando:
        raise ValueError(
            f"Aba '{aba_usada}' não contém as colunas: {faltando}. "
            f"Colunas encontradas: {list(df.columns)}"
        )

    # 5. Normalizar nomes de serviço (remove acentuação inconsistente)
    df["Tipo_Servico"] = df["Tipo_Servico"].str.strip()
    df["Tipo_Servico"] = df["Tipo_Servico"].apply(
        lambda v: _SERVICO_MAP.get(str(v).lower(), v)
    )

    # 6. Garantir H_Advogado mesmo em bases sem essa coluna
    if "H_Advogado" not in df.columns:
        df["H_Advogado"] = 0.0

    return df, aba_usada


def _empacotar_resultado(m1, y1, agg, variaveis):
    """Converte os objetos statsmodels para dict serializável pela API."""
    p_ideal_6, cpc = preco_ideal(m1, agg, margem_alvo=0.06)
    elast = elasticidades(m1, agg, variaveis)
    mae = mean_absolute_error(y1, m1.fittedvalues)

    betas = list(m1.params)
    return {
        "n_observacoes": int(len(agg)),
        "variaveis": variaveis,
        "beta0": round(betas[0], 2),
        "beta1": round(betas[1], 2),
        "beta2": round(betas[2], 2),
        "beta3": round(betas[3], 2),
        "beta4": round(betas[4], 2) if len(betas) > 4 else None,
        "r2":          round(float(m1.rsquared), 4),
        "r2_ajustado": round(float(m1.rsquared_adj), 4),
        "mae":         round(float(mae), 2),
        "elasticidades": {k: round(v, 4) for k, v in elast.items()},
        "custo_por_contrato": round(float(cpc), 2),
        "preco_ideal_6":      round(float(p_ideal_6), 2),
        "preco_ideal_10":     round(float(cpc / 0.90), 2),
        "preco_ideal_15":     round(float(cpc / 0.85), 2),
        "margem_observada":   round(float(agg["Margem_PCT"].mean()), 4),
        "margem_rs_media":    round(float(agg["Margem_RS"].mean()), 2),
    }


def rodar_regressao(caminho_excel):
    """
    Ponto de entrada da API: carrega o Excel, roda as três regressões
    usando as funções do Léo e retorna dict com resultados por serviço.
    """
    df, aba_usada = carregar_df(caminho_excel)

    servicos_disponiveis = df["Tipo_Servico"].unique().tolist()
    resultados = {"_meta": {"aba_usada": aba_usada, "servicos_encontrados": servicos_disponiveis}}

    # Expansão
    if "Expansão" in servicos_disponiveis:
        agg_exp  = agregar(df, "Expansão")
        vars_exp = ["Qtd_Contratos", "H_Total", "Num_Mes"]
        m1_exp, _, y1_exp, _ = rodar_ols(agg_exp, vars_exp)
        resultados["expansao"] = _empacotar_resultado(m1_exp, y1_exp, agg_exp, vars_exp)

    # Formatação
    if "Formatação" in servicos_disponiveis:
        agg_fmt  = agregar(df, "Formatação")
        vars_fmt = ["Qtd_Contratos", "H_Total", "H_Advogado", "Num_Mes"]
        m1_fmt, _, y1_fmt, _ = rodar_ols(agg_fmt, vars_fmt)
        resultados["formatacao"] = _empacotar_resultado(m1_fmt, y1_fmt, agg_fmt, vars_fmt)

    # Validação
    if "Validação" in servicos_disponiveis:
        agg_val  = agregar(df, "Validação")
        vars_val = ["Qtd_Contratos", "H_Total", "Num_Mes"]
        m1_val, _, y1_val, _ = rodar_ols(agg_val, vars_val)
        resultados["validacao"] = _empacotar_resultado(m1_val, y1_val, agg_val, vars_val)

    if not any(k in resultados for k in ("expansao", "formatacao", "validacao")):
        raise ValueError(
            f"Nenhum serviço reconhecido encontrado. "
            f"Valores em Tipo_Servico: {servicos_disponiveis}"
        )

    # Preview das primeiras 200 linhas do df bruto para visualização no frontend
    colunas_preview = [c for c in [
        "Mês", "Franquia", "Tipo_Servico", "Qtd_Contratos",
        "H_Total", "H_Advogado", "Total_Custos", "Receita_Total", "Margem_RS"
    ] if c in df.columns]
    resultados["_preview"] = df[colunas_preview].head(200).to_dict("records")

    return resultados
