# Em relatorios/views.py

from django.shortcuts import render
from django.db.models import Avg, F, Q
from manejo.models import Manejo
from boi.models import Boi
from .forms import PeriodoForm


def relatorio_medias_peso(request):
    """
    Esta view calcula e exibe as médias de peso para os manejos
    de saída e de movimentação em duas seções separadas.
    """
    
    # --- CÁLCULO PARA MANEJOS DE SAÍDA ---
    manejos_saida = Manejo.objects.filter(
        tipo_manejo__nome_tipo_manejo__iexact='saida'
    ).annotate(
        media_peso_saida=Avg('bois_em_manejo__boi__peso_saida')
    ).order_by('-data_manejo')

    # --- CÁLCULO PARA MANEJOS DE MOVIMENTAÇÃO (COM O CAMINHO CORRIGIDO) ---
    manejos_movimentacao = Manejo.objects.filter(
        tipo_manejo__nome_tipo_manejo__iexact='movimentacao'
    ).annotate(
        media_peso_movimentacao=Avg(
            # CORREÇÃO: trocamos 'pesomovimentacao' por 'pesagens'
            'bois_em_manejo__boi__pesagens__peso_movimentacao',
            filter=Q(
                # CORREÇÃO: trocamos 'pesomovimentacao' por 'pesagens' aqui também
                bois_em_manejo__boi__pesagens__data_movimentacao=F('data_manejo')
            )
        )
    ).order_by('-data_manejo')

    context = {
        'manejos_saida': manejos_saida,
        'manejos_movimentacao': manejos_movimentacao,
    }
    
    return render(request, 'relatorio/mediapeso.html', context)

def relatorio_mortalidade(request):
    resultado = None

    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            data_inicio = form.cleaned_data['data_inicio']
            data_fim = form.cleaned_data['data_fim']

            # Bois vivos no início
            rebanho_inicial = Boi.objects.filter(
                data_entrada__lt=data_inicio
            ).filter(
                Q(data_saida__isnull=True) | Q(data_saida__gt=data_inicio),
                Q(data_morte__isnull=True) | Q(data_morte__gt=data_inicio)
            ).count()

            # Entradas no período
            entradas = Boi.objects.filter(data_entrada__range=(data_inicio, data_fim)).count()

            # Mortes no período
            mortes = Boi.objects.filter(data_morte__range=(data_inicio, data_fim)).count()

            # Rebanho acumulado
            rebanho_acumulado = rebanho_inicial + entradas

            taxa_mortalidade = (mortes / rebanho_acumulado) * 100 if rebanho_acumulado > 0 else 0

            resultado = {
                'rebanho_inicial': rebanho_inicial,
                'entradas': entradas,
                'rebanho_acumulado': rebanho_acumulado,
                'mortes': mortes,
                'taxa': round(taxa_mortalidade, 2),
            }
    else:
        form = PeriodoForm()

    return render(request, 'relatorio/relatorio_mortalidade.html', {'form': form, 'resultado': resultado})