
from django.urls import path
from relatorio.views import relatorio_medias_peso, relatorio_mortalidade

urlpatterns = [
    path('mediapeso/', relatorio_medias_peso, name='relatoriomedia'),
    path('relatorios/mortalidade/', relatorio_mortalidade, name='relatorio_mortalidade'),
    
   
]