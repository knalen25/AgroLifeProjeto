# Generated by Django 5.2.2 on 2025-06-06 05:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('boi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Doenca',
            fields=[
                ('iddoenca', models.AutoField(help_text='Identificador único da doença.', primary_key=True, serialize=False)),
                ('nome_doenca', models.CharField(help_text="Nome da doença (por exemplo: 'Mastite', 'Pneumonia').", max_length=50)),
            ],
            options={
                'db_table': 'doenca',
            },
        ),
        migrations.CreateModel(
            name='Laboratorio',
            fields=[
                ('idlaboratorio', models.AutoField(help_text='Identificador único do laboratório.', primary_key=True, serialize=False)),
                ('nome_laboratorio', models.CharField(help_text='Nome do laboratório fabricante.', max_length=50)),
            ],
            options={
                'db_table': 'laboratorio',
            },
        ),
        migrations.CreateModel(
            name='PrincipioAtivo',
            fields=[
                ('idprincipio_ativo', models.AutoField(help_text='Identificador único do princípio ativo.', primary_key=True, serialize=False)),
                ('nome_principio_ativo', models.CharField(help_text="Nome do princípio ativo (por exemplo: 'Penicilina', 'Ivermectina').", max_length=45)),
            ],
            options={
                'db_table': 'principio_ativo',
            },
        ),
        migrations.CreateModel(
            name='ResponsavelTecnico',
            fields=[
                ('idresponsavel_tecnico', models.AutoField(help_text='Identificador único do responsável técnico.', primary_key=True, serialize=False)),
                ('nome_responsavel', models.CharField(help_text='Nome do responsável técnico pela aplicação.', max_length=50)),
            ],
            options={
                'db_table': 'responsavel_tecnico',
            },
        ),
        migrations.CreateModel(
            name='TipoMedicamento',
            fields=[
                ('idtipo_medicamento', models.AutoField(help_text='Identificador único do tipo de medicamento.', primary_key=True, serialize=False)),
                ('nome_medicamento', models.CharField(help_text="Nome do tipo de medicamento (por exemplo: 'Antibiótico', 'Vacina').", max_length=50)),
            ],
            options={
                'db_table': 'tipo_medicamento',
            },
        ),
        migrations.CreateModel(
            name='AplicacaoEvento',
            fields=[
                ('idaplicacao_evento', models.AutoField(help_text='Identificador único da aplicação de medicamento.', primary_key=True, serialize=False)),
                ('data_aplicacao_medicamento', models.DateField(help_text='Data em que o medicamento foi aplicado.')),
                ('boi', models.ForeignKey(help_text='Boi que recebeu a aplicação do medicamento.', on_delete=django.db.models.deletion.PROTECT, related_name='aplicacoes', to='boi.boi')),
                ('doenca', models.ForeignKey(blank=True, help_text='Doença que motivou a aplicação (opcional).', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='aplicacoes_doenca', to='medicamento.doenca')),
            ],
            options={
                'db_table': 'aplicacao_medicamento',
            },
        ),
        migrations.CreateModel(
            name='Medicamento',
            fields=[
                ('idmedicamento', models.AutoField(help_text='Identificador único do medicamento.', primary_key=True, serialize=False)),
                ('nome_medicamento', models.CharField(help_text='Nome comercial do medicamento.', max_length=50)),
                ('dias_de_carencia', models.IntegerField(help_text='Período de carência (em dias) após aplicação do medicamento.')),
                ('preco_ml', models.DecimalField(decimal_places=2, help_text='Preço do medicamento por ml.', max_digits=4)),
                ('laboratorio', models.ForeignKey(help_text='Laboratório responsável pela fabricação do medicamento.', on_delete=django.db.models.deletion.PROTECT, related_name='medicamentos_por_laboratorio', to='medicamento.laboratorio')),
                ('principio_ativo', models.ForeignKey(help_text='Princípio ativo presente no medicamento.', on_delete=django.db.models.deletion.PROTECT, related_name='medicamentos_por_principio', to='medicamento.principioativo')),
                ('tipo_medicamento', models.ForeignKey(help_text='Tipo do medicamento.', on_delete=django.db.models.deletion.PROTECT, related_name='medicamentos_por_tipo', to='medicamento.tipomedicamento')),
            ],
            options={
                'db_table': 'medicamento',
            },
        ),
        migrations.CreateModel(
            name='MedicamentoAplicado',
            fields=[
                ('idmedicamento_aplicado', models.AutoField(primary_key=True, serialize=False)),
                ('dose_aplicada', models.DecimalField(decimal_places=2, help_text='Dose específica deste medicamento (em ml, mg, etc.)', max_digits=5)),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='medicamento.aplicacaoevento')),
                ('medicamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='medicamento.medicamento')),
            ],
            options={
                'verbose_name': 'Medicamento Aplicado',
                'verbose_name_plural': 'Medicamentos Aplicados',
                'db_table': 'medicamento_aplicado',
                'unique_together': {('evento', 'medicamento')},
            },
        ),
        migrations.AddField(
            model_name='aplicacaoevento',
            name='medicamento',
            field=models.ManyToManyField(related_name='eventos_associados', through='medicamento.MedicamentoAplicado', to='medicamento.medicamento'),
        ),
        migrations.AddField(
            model_name='aplicacaoevento',
            name='responsavel_tecnico',
            field=models.ForeignKey(blank=True, help_text='Pessoa responsável pela aplicação do medicamento.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='aplicacoes_por_tecnico', to='medicamento.responsaveltecnico'),
        ),
    ]
