# Generated by Django 3.2.25 on 2024-11-29 18:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_inventario_disponible'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]