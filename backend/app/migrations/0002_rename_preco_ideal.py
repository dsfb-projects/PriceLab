from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resultadoregressao',
            old_name='preco_ideal_30',
            new_name='preco_ideal_6',
        ),
    ]
