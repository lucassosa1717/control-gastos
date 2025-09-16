# Generated manually to remove gamification tables
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gastitos', '0009_metaahorro_moneda'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS gastitos_logrousuario;",
            reverse_sql=""
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS gastitos_logro;",
            reverse_sql=""
        ),
        migrations.RunSQL(
            "DROP TABLE IF EXISTS gastitos_racha;",
            reverse_sql=""
        ),
    ]