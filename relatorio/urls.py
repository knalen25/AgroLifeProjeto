
from django.urls import path
from relatorio.views import relatorio_medias_peso

urlpatterns = [
    path('mediapeso/', relatorio_medias_peso, name='relatoriomedia'),
]