from django.views import View
from django.shortcuts import render, redirect
from movimentacao.forms import TrocaCurralForm
from boi.models import Boi
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from movimentacao.models import Movimentacao
from django.db.models import Q

class MovimentacaoView(View):
    template_name = "movimentacao/criarmovimentacao.html"

    def get(self, request):
        form = TrocaCurralForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TrocaCurralForm(request.POST)
        if form.is_valid():
            movimentacao = form.save()

            lote_destino = movimentacao.lote_destino
            lote_destino.curral = movimentacao.curral_destino
            lote_destino.save(update_fields=['curral'])
            
            if movimentacao.lote_origem != movimentacao.lote_destino:
                Boi.objects.filter(lote=movimentacao.lote_origem).update(lote=movimentacao.lote_destino)

            return redirect('listamovimentacao')
        return render(request, self.template_name, {'form': form})


#revisar o querySet
class MovimentacaoListView(ListView):
    model = Movimentacao
    template_name = 'movimentacao/listamovimentacao.html'
    context_object_name = 'movimentacoes'
    paginate_by = 10 

    def get_queryset(self):
        
        queryset = super().get_queryset().select_related(
            'status', 'lote_origem', 'lote_destino', 'curral_destino'
        )

        
        search_query = self.request.GET.get('q')
        
        if search_query:
           
            query_filter = (
                Q(lote_origem__nome_lote__icontains=search_query) |
                Q(lote_destino__nome_lote__icontains=search_query) |
                Q(curral_destino__nome_curral__icontains=search_query)
            )
            queryset = queryset.filter(query_filter)

   
        return queryset.order_by('-data_movimentacao')

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context


class MovimentacaoDetailView(DetailView):
    model = Movimentacao
    template_name = 'movimentacao/detalhemovimentacao.html'
    context_object_name = 'movimentacao'

class MovimentacaoUpdateView(UpdateView):
    model = Movimentacao
    form_class = TrocaCurralForm
    template_name = 'movimentacao/editarmovimentacao.html'
    context_object_name = 'movimentacao'
    success_url = reverse_lazy('listamovimentacao')

class MovimentacaoDeleteView(DeleteView):
    model = Movimentacao
    template_name = 'movimentacao/deletarmovimentacao.html'
    context_object_name = 'movimentacao'
    success_url = reverse_lazy('listamovimentacao')    
