from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Sum, Avg, Count
from lote.forms import LoteModelForm
from lote.models import Lote
from boi.models import Boi
from django.views.generic import DetailView, DeleteView, UpdateView, CreateView, ListView
from django.db.models import Q



class ListaLoteView(ListView):
    model = Lote
    template_name = 'lote/listalote.html'
    context_object_name = 'lotes'

    def get_queryset(self):
        
        queryset = super().get_queryset()

        
        queryset = queryset.annotate(
            total_animais=Count('bois_por_lote'),
        )
        
        
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(nome_lote__icontains=search) |
                Q(curral__nome_curral__icontains=search)
            )
        
       
        return queryset.order_by('idlote')
                
class LoteCreateView(CreateView):
    model = Lote
    form_class = LoteModelForm
    template_name = 'lote/criarlote.html'
    success_url = '/listalote/'

class LoteDetailView(DetailView):
    model = Lote
    template_name = 'lote/detalhelote.html'

class LoteUpdateView(UpdateView):
    model = Lote
    form_class = LoteModelForm
    template_name = 'lote/atualizarlote.html'
    success_url = '/listalote/'
    
class LoteDeleteView(DeleteView):
    model = Lote
    template_name = 'lote/deletarlote.html'
    success_url = '/listalote/'