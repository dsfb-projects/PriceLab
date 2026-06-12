from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_resultadoregressao_stats_extras'),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadedbase',
            name='premissas',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
