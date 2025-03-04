# Generated by Django 5.1.4 on 2024-12-20 16:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Negocio', '0004_alter_tienda_coordenada_latitud_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='ciudad',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='coordenada_latitud',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='coordenada_longitud',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='direccion_calle',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='direccion_numero',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='profile',
            name='pais',
            field=models.CharField(default='Argentina', max_length=50),
        ),
        migrations.AddField(
            model_name='profile',
            name='rango_busqueda_km',
            field=models.FloatField(default=10),
        ),
    ]
