# Generated by Django 5.1.4 on 2025-01-17 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Negocio', '0025_alter_tienda_dias_atencion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tienda',
            name='dias_atencion',
            field=models.CharField(choices=[('lunes_a_viernes', 'Lunes a Viernes'), ('lunes_a_sabado', 'Lunes a Sabado'), ('todos_los_dias', 'Todos los dias')], default='lunes_a_viernes', max_length=50),
        ),
    ]
