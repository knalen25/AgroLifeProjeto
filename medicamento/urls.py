from django.urls import path
from medicamento.views import (MedicamentoCreateView, MedicamentoDeleteView, MedicamentoListView,MedicamentoDetailView, MedicamentoUpdateView , AplicacaoEventoCreateView, AplicacaoEventoDeleteView, AplicacaoEventoListView, AplicacaoEventoDetailView, AplicacaoEventoUpdateView)

urlpatterns = [
    path('criar/', MedicamentoCreateView.as_view(), name='criarmedicamento'),
    path('listar/', MedicamentoListView.as_view(), name='listamedicamento'),
    path('deletar/<int:pk>/', MedicamentoDeleteView.as_view(), name='deletarmedicamento'),
    path('detalhe/<int:pk>/', MedicamentoDetailView.as_view(), name='detalhemedicamento'),
    path('update/<int:pk>/', MedicamentoUpdateView.as_view(), name='updatemedicamento'),

    path('aplicacao/criar/', AplicacaoEventoCreateView.as_view(), name='criaraplicacao'),
    path('aplicacao/listar/', AplicacaoEventoListView.as_view(), name='listaaplicacao'),
    path('aplicacao/deletar/<int:pk>/', AplicacaoEventoDeleteView.as_view(), name='deletaraplicacao'),
    path('aplicacao/detalhe/<int:pk>/', AplicacaoEventoDetailView.as_view(), name='detalheaplicacao'),
    path('aplicacao/update/<int:pk>/', AplicacaoEventoUpdateView.as_view(), name='atualizaraplicacao'),
]