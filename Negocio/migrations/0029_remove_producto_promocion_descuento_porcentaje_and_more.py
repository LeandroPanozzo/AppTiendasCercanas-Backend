# Generated by Django 5.1.4 on 2025-01-20 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Negocio', '0028_producto_promocion_descuento_porcentaje_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='promocion_descuento_porcentaje',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='promocion_unidad_descuento',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='promocion_unidades',
        ),
        migrations.AlterField(
            model_name='producto',
            name='permite_reservas',
            field=models.BooleanField(default=True, help_text='Permite reservar este producto específico'),
        ),
    ]
