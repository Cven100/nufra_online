# Generated by Django 3.2.25 on 2024-12-03 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_ordenescompra_cantidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='rut',
            field=models.CharField(max_length=14, unique=True),
        ),
    ]
