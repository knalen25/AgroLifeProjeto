# Em relatorios/views.py

from django.shortcuts import render
from django.db.models import Avg, F, Q
from manejo.models import Manejo

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