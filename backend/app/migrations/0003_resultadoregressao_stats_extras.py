from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_preco_ideal'),
    ]

    operations = [
        migrations.AddField(
            model_name='resultadoregressao',
            name='stats_extras',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
