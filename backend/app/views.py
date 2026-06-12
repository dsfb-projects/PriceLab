import json
import os
import pandas as pd

from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import UploadedBase, ResultadoRegressao
from .regression import rodar_regressao, carregar_df

_SERVICOS = ('expansao', 'formatacao', 'validacao')


@api_view(['POST'])
def login_view(request):
    """
    Login simples com credencial única, validada contra variáveis de ambiente.
    Sobrevive a deploys no Render (não depende do SQLite).
    Defaults para dev local: pricelab / fae2026
    """
    usuario = str(request.data.get('usuario', '')).strip()
    senha = str(request.data.get('senha', ''))
    esperado_usuario = os.environ.get('APP_USUARIO', 'pricelab')
    esperada_senha = os.environ.get('APP_SENHA', 'fae2026')
    if usuario == esperado_usuario and senha == esperada_senha:
        return Response({'ok': True})
    return Response({'erro': 'Usuário ou senha inválidos.'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_base(request):
    arquivo = request.FILES.get('arquivo')
    if not arquivo:
        return Response({'erro': 'Nenhum arquivo enviado.'}, status=status.HTTP_400_BAD_REQUEST)

    extensao = arquivo.name.rsplit('.', 1)[-1].lower()
    if extensao not in ('xlsx', 'xls'):
        return Response({'erro': 'Formato inválido. Envie um arquivo .xlsx ou .xls.'}, status=status.HTTP_400_BAD_REQUEST)

    base = UploadedBase.objects.create(arquivo=arquivo)

    try:
        todos = rodar_regressao(base.arquivo.path)
    except Exception as e:
        base.delete()
        return Response({'erro': f'Erro ao processar a base: {str(e)}'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    # Salva coeficientes por serviço no banco (ignora chaves internas _preview/_meta)
    _EXTRAS = ('pvalues', 'f_stat', 'f_pvalue', 'rmse', 'r2_m2', 'mae_m2_pp',
               'variaveis', 'n_observacoes', 'preco_ideal_10', 'preco_ideal_15')
    for sv in _SERVICOS:
        if sv not in todos:
            continue
        d = todos[sv]
        ResultadoRegressao.objects.create(
            base=base,
            servico=sv,
            beta0=d['beta0'], beta1=d['beta1'], beta2=d['beta2'], beta3=d['beta3'],
            beta4=d.get('beta4'),
            r2=d['r2'], r2_ajustado=d['r2_ajustado'], mae=d['mae'],
            elasticidades=d['elasticidades'],
            custo_por_contrato=d['custo_por_contrato'],
            preco_ideal_6=d['preco_ideal_6'],
            margem_observada=d['margem_observada'],
            stats_extras={k: d[k] for k in _EXTRAS if k in d},
        )

    resultados = {sv: todos[sv] for sv in _SERVICOS if sv in todos}
    return Response({
        'base_id': base.pk,
        'resultados': resultados,
        'df_preview': todos.get('_preview', []),
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def resultados_latest(request):
    base = UploadedBase.objects.first()
    if not base:
        return Response({'erro': 'Nenhuma base enviada ainda.'}, status=status.HTTP_404_NOT_FOUND)

    resultados = {}
    for r in base.resultados.all():
        resultados[r.servico] = {
            'beta0': r.beta0, 'beta1': r.beta1, 'beta2': r.beta2, 'beta3': r.beta3, 'beta4': r.beta4,
            'r2': r.r2, 'r2_ajustado': r.r2_ajustado, 'mae': r.mae,
            'elasticidades': r.elasticidades,
            'custo_por_contrato': r.custo_por_contrato,
            'preco_ideal_6': r.preco_ideal_6,
            'margem_observada': r.margem_observada,
            **(r.stats_extras or {}),
        }

    # Recarrega o df do arquivo salvo para gerar o preview
    df_preview = []
    try:
        df, _ = carregar_df(base.arquivo.path)
        colunas = [c for c in [
            "Mês", "Franquia", "Tipo_Servico", "Qtd_Contratos",
            "H_Total", "H_Advogado", "Total_Custos", "Receita_Total", "Margem_RS"
        ] if c in df.columns]
        df_preview = df[colunas].head(200).to_dict("records")
    except Exception:
        pass

    return Response({
        'base_id': base.pk,
        'enviado_em': base.enviado_em,
        'resultados': resultados,
        'df_preview': df_preview,
    })
