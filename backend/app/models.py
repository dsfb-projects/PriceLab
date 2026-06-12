from django.db import models


class UploadedBase(models.Model):
    arquivo = models.FileField(upload_to='bases/')
    enviado_em = models.DateTimeField(auto_now_add=True)

    # Premissas de negócio lidas da aba 2_Premissas_v4 (se existir no Excel)
    premissas = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ['-enviado_em']

    def __str__(self):
        return f"Base #{self.pk} — {self.enviado_em:%d/%m/%Y %H:%M}"


class ResultadoRegressao(models.Model):
    SERVICOS = [
        ('expansao', 'Expansão'),
        ('formatacao', 'Formatação'),
        ('validacao', 'Validação'),
    ]

    base = models.ForeignKey(UploadedBase, on_delete=models.CASCADE, related_name='resultados')
    servico = models.CharField(max_length=20, choices=SERVICOS)
    calculado_em = models.DateTimeField(auto_now_add=True)

    # Coeficientes do Modelo 1 (Y = Total_Custos)
    beta0 = models.FloatField()
    beta1 = models.FloatField()
    beta2 = models.FloatField()
    beta3 = models.FloatField()
    beta4 = models.FloatField(null=True, blank=True)  # só Formatação tem H_Advogado

    # Qualidade do ajuste
    r2 = models.FloatField()
    r2_ajustado = models.FloatField()
    mae = models.FloatField()

    # Elasticidades (JSON)
    elasticidades = models.JSONField(default=dict)

    # Estatísticas adicionais do código final do Léo:
    # pvalues, f_stat, f_pvalue, rmse, r2_m2, mae_m2_pp, variaveis, n_observacoes
    stats_extras = models.JSONField(default=dict, blank=True)

    # Precificação
    custo_por_contrato = models.FloatField()
    preco_ideal_6 = models.FloatField()
    margem_observada = models.FloatField()

    class Meta:
        ordering = ['-calculado_em']

    def __str__(self):
        return f"{self.get_servico_display()} — Base #{self.base_id}"
