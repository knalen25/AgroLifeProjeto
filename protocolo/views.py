from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from protocolo.models import ProtocoloSanitario
from protocolo.forms import ProtocoloSanitarioForm, ProtocoloMedicamentoFormSet
from django.views.generic import ListView, DeleteView, UpdateView, DetailView
from django.db.models import Q


class ProtocoloCreateView(View):
    template_name = 'protocolo/criarprotocolo.html'

    def get(self, request):
        protocolo_form = ProtocoloSanitarioForm()
        formset = ProtocoloMedicamentoFormSet(prefix='form')
        return render(request, self.template_name, {
            'protocolo_form': protocolo_form,
            'formset': formset,
            'medicamentos': [],
        })

    def post(self, request):
        protocolo_form = ProtocoloSanitarioForm(request.POST)
        formset = ProtocoloMedicamentoFormSet(request.POST, prefix='form')

        if protocolo_form.is_valid() and formset.is_valid():
            protocolo = protocolo_form.save()
            formset.instance = protocolo
            formset.save()

            medicamentos = protocolo.protocolos_por_sanitario.select_related('medicamento')

            return redirect(reverse_lazy('listaprotocolo'))

        return render(request, self.template_name, {
            'protocolo_form': protocolo_form,
            'formset': formset,
            'medicamentos': []
        })

class ProtocoloListView(ListView):
    model = ProtocoloSanitario
    template_name = 'protocolo/listaprotocolo.html'
    context_object_name = 'protocolos'
    paginate_by = 10 

    def get_queryset(self):
        
        queryset = super().get_queryset().select_related('responsavel_tecnico').prefetch_related('protocolos_por_sanitario__medicamento')

        
        search_query = self.request.GET.get('q') 
        
        if search_query:
            
            query_filter = (
                Q(nome_protocolo__icontains=search_query) |
                Q(motivo_protocolo__icontains=search_query) |
                Q(responsavel_tecnico__nome_responsavel_tecnico__icontains=search_query) 
            )
            queryset = queryset.filter(query_filter)

        return queryset.order_by('-idprotocolo_sanitario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class ProtocoloUpdateView(View):
    template_name = 'protocolo/atualizarprotocolo.html'

    def get(self, request, pk):
        protocolo = get_object_or_404(ProtocoloSanitario, pk=pk)
        protocolo_form = ProtocoloSanitarioForm(instance=protocolo)
        formset = ProtocoloMedicamentoFormSet(instance=protocolo, prefix='form')
        return render(request, self.template_name, {
            'protocolo_form': protocolo_form,
            'formset': formset,
            'protocolo': protocolo,
        })

    def post(self, request, pk):
        protocolo = get_object_or_404(ProtocoloSanitario, pk=pk)
        protocolo_form = ProtocoloSanitarioForm(request.POST, instance=protocolo)
        formset = ProtocoloMedicamentoFormSet(request.POST, instance=protocolo, prefix='form')

        if protocolo_form.is_valid() and formset.is_valid():
            protocolo_form.save()
            formset.save()
            return redirect('listaprotocolo')

        return render(request, self.template_name, {
            'protocolo_form': protocolo_form,
            'formset': formset,
            'protocolo': protocolo,
        })
        
class ProtocoloDeleteView(DeleteView):
    model = ProtocoloSanitario
    template_name = 'protocolo/deletarprotocolo.html'
    success_url = reverse_lazy('listaprotocolo')
    context_object_name = 'protocolo'
    
class ProtocoloDetailView(DetailView):
    model = ProtocoloSanitario
    template_name = 'protocolo/detalheprotocolo.html'
    context_object_name = 'protocolo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['medicamentos'] = self.object.protocolos_por_sanitario.select_related('medicamento')
        return context 