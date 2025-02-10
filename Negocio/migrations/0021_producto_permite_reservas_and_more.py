# Generated by Django 5.1.4 on 2025-01-11 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Negocio', '0020_remove_reserva_estado_alter_reserva_fecha_reserva_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='permite_reservas',
            field=models.BooleanField(default=True, help_text='Permite reservar este producto específico'),
        ),
        migrations.AddField(
            model_name='reserva',
            name='confirmacion_retirada',
            field=models.BooleanField(default=False, help_text='Confirmación por parte del propietario de la tienda'),
        ),
        migrations.AddField(
            model_name='reserva',
            name='estado',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('confirmada', 'Confirmada'), ('cancelada', 'Cancelada'), ('retirada', 'Retirada'), ('vencida', 'Vencida')], default='pendiente', max_length=20),
        ),
        migrations.AddField(
            model_name='reserva',
            name='fecha_limite',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='tienda',
            name='permite_reservas',
            field=models.BooleanField(default=True, help_text='Habilita/deshabilita las reservas para toda la tienda'),
        ),
    ]
