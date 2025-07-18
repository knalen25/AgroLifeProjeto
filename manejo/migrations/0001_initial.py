# Generated by Django 5.2.2 on 2025-06-06 05:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('boi', '0001_initial'),
        ('protocolo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatusManejo',
            fields=[
                ('idstatus_manejo', models.AutoField(help_text='Identificador único do status de manejo.', primary_key=True, serialize=False)),
                ('nome_status_manejo', models.CharField(help_text="Descrição do status do manejo (por exemplo: 'Programado', 'Concluído').", max_length=45)),
            ],
            options={
                'db_table': 'status_manejo',
            },
        ),
        migrations.CreateModel(
            name='TipoManejo',
            fields=[
                ('idtipo_manejo', models.AutoField(help_text='Identificador único do tipo de manejo.', primary_key=True, serialize=False)),
                ('nome_tipo_manejo', models.CharField(help_text="Descrição do tipo de manejo (por exemplo: 'Pesagem', 'Vacinação').", max_length=10)),
            ],
            options={
                'db_table': 'tipo_manejo',
            },
        ),
        migrations.CreateModel(
            name='Manejo',
            fields=[
                ('idManejo', models.AutoField(help_text='Identificador único do manejo.', primary_key=True, serialize=False)),
                ('data_manejo', models.DateField(help_text='Data em que o manejo foi realizado.')),
                ('protocolo_sanitario', models.ForeignKey(help_text='Protocolo sanitário utilizado no manejo.', on_delete=django.db.models.deletion.PROTECT, related_name='manejos_protocolo', to='protocolo.protocolosanitario')),
                ('status_manejo', models.ForeignKey(help_text='Status atual do manejo.', on_delete=django.db.models.deletion.PROTECT, related_name='manejos_por_status', to='manejo.statusmanejo')),
                ('tipo_manejo', models.ForeignKey(help_text='Tipo de manejo aplicado.', on_delete=django.db.models.deletion.PROTECT, related_name='manejos_por_tipo', to='manejo.tipomanejo')),
            ],
            options={
                'db_table': 'Manejo',
            },
        ),
        migrations.CreateModel(
            name='BoiManejo',
            fields=[
                ('idboi_manejo', models.AutoField(help_text='Identificador único da associação entre boi e manejo.', primary_key=True, serialize=False)),
                ('boi', models.ForeignKey(help_text='Boi que participou do manejo.', on_delete=django.db.models.deletion.PROTECT, related_name='manejos', to='boi.boi')),
                ('protocolo_sanitario', models.ForeignKey(help_text='Protocolo sanitário utilizado no manejo.', on_delete=django.db.models.deletion.PROTECT, related_name='bois_protocolo', to='protocolo.protocolosanitario')),
                ('manejo', models.ForeignKey(help_text='Manejo ao qual o boi está vinculado.', on_delete=django.db.models.deletion.PROTECT, related_name='bois_em_manejo', to='manejo.manejo')),
            ],
            options={
                'db_table': 'boi_manejo',
            },
        ),
    ]
