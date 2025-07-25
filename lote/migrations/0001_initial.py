# Generated by Django 5.2.2 on 2025-06-06 05:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('curral', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lote',
            fields=[
                ('idlote', models.AutoField(help_text='Identificador único do lote.', primary_key=True, serialize=False)),
                ('nome_lote', models.CharField(help_text='Nome ou código do lote.', max_length=30)),
                ('data_inicio_lote', models.DateField(help_text='Data de início de utilização do lote.')),
                ('ativo', models.BooleanField(default=True, help_text='Indica se o lote está ativo (True) ou inativo (False).')),
                ('curral', models.ForeignKey(help_text='Curral ao qual o lote está vinculado.', on_delete=django.db.models.deletion.PROTECT, related_name='lotes', to='curral.curral')),
            ],
            options={
                'db_table': 'Lote',
            },
        ),
    ]
