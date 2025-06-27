from django.urls import reverse_lazy
from django.shortcuts import render
from boi.forms import BoiModelForm, BoiMorteForm
from boi.models import Boi, StatusBoi
from django.views.generic import DetailView, DeleteView, UpdateView, CreateView, ListView
from django.db.models import Q
from django.utils import timezone
from decimal import Decimal

class ListaBoiView(ListView):
    model = Boi
    template_name = 'boi/listaboi.html'
    context_object_name = 'bois'

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            status_boi__nome_status__in=['Ativo', 'Vendido']
        ).order_by('brinco')

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(brinco__icontains=search) |
                Q(fornecedor__nome_fornecedor__icontains=search) |
                Q(status_boi__nome_status__icontains=search) |
                Q(lote__nome_lote__icontains=search) |
                Q(data_entrada__icontains=search)
            ).order_by('brinco')

        return queryset
    
class BoiCreateView(CreateView):
    model = Boi
    form_class = BoiModelForm
    template_name = 'boi/nascimentoboi.html'
    success_url = reverse_lazy('listaboi')

# class BoiDetailView(DetailView):
#     model = Boi
#     template_name = 'boi/detalheboi.html'
#     context_object_name = 'boi'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         boi = self.get_object()
#         ultima_proj = boi.projecoes_peso.order_by('-data_projetado').first()
#         context['peso_projetado'] = ultima_proj
#         return context
class BoiDetailView(DetailView):
    model = Boi
    template_name = 'boi/detalheboi.html'
    context_object_name = 'boi'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        boi = self.get_object()

        

        
        ultima_pesagem = boi.pesagens.order_by('-data_movimentacao').first()

        if ultima_pesagem:
            peso_base = ultima_pesagem.peso_movimentacao
            data_base = ultima_pesagem.data_movimentacao
        else:
            peso_base = boi.peso_entrada
            data_base = boi.data_entrada

        
        gmd_alvo = Decimal('0.0')
        if boi.lote and boi.lote.curral and boi.lote.curral.tipo_curral:
            tipo_curral_nome = boi.lote.curral.tipo_curral.nome_tipo_curral.lower()
            if 'pasto' in tipo_curral_nome:
                gmd_alvo = Decimal('0.85')
            elif 'confinamento' in tipo_curral_nome:
                gmd_alvo = Decimal('1.3')

        
        data_final_projecao = timezone.now().date() 
        is_finalizado = False 

        if boi.status_boi.nome_status == 'Vendido' and boi.data_saida:
            data_final_projecao = boi.data_saida
            is_finalizado = True
        elif boi.status_boi.nome_status == 'Morto' and boi.data_morte:
            data_final_projecao = boi.data_morte
            is_finalizado = True
        
        
        dias_desde_base = (data_final_projecao - data_base).days if data_final_projecao > data_base else 0
        ganho_projetado = dias_desde_base * gmd_alvo
        peso_final_projetado = peso_base + ganho_projetado

        
        context['dados_projecao'] = {
            'peso_base': peso_base,
            'data_base': data_base,
            'gmd_alvo': gmd_alvo,
            'dias_passados': dias_desde_base,
            'peso_atual_projetado': peso_final_projetado,
            'is_finalizado': is_finalizado, 
            'data_final_projecao': data_final_projecao
        }

        
        historico = []
        if boi.data_entrada:
            historico.append({'data': boi.data_entrada, 'tipo': 'Entrada no Sistema', 'descricao': f"Animal registrado com peso de entrada de {boi.peso_entrada} kg."})
        if boi.data_nascimento:
            historico.append({'data': boi.data_nascimento, 'tipo': 'Nascimento', 'descricao': 'Data de nascimento registrada.'})
        for pesagem in boi.pesagens.all():
            historico.append({'data': pesagem.data_movimentacao, 'tipo': 'Pesagem', 'descricao': f"Pesagem de movimentação registrada com {pesagem.peso_movimentacao} kg."})
        for boi_manejo in boi.manejos.select_related('manejo__tipo_manejo').all():
            historico.append({'data': boi_manejo.manejo.data_manejo, 'tipo': 'Manejo', 'descricao': f"Participou do Manejo de '{boi_manejo.manejo.tipo_manejo.nome_tipo_manejo}' (ID: {boi_manejo.manejo.idManejo})"})
        if boi.data_saida:
             historico.append({'data': boi.data_saida, 'tipo': 'Saída', 'descricao': f"Venda registrada com peso de saída de {boi.peso_saida} kg."})
        if boi.data_morte:
             historico.append({'data': boi.data_morte, 'tipo': 'Morte', 'descricao': f"Morte registrada. Motivo: {boi.motivo_morte}"})
        
        context['historico_ordenado'] = sorted(historico, key=lambda e: e['data'], reverse=True)

        return context
    

class BoiUpdateView(UpdateView):
    model = Boi
    form_class = BoiModelForm
    template_name = 'boi/atualizarboi.html'
    success_url = reverse_lazy('listaboi')

class BoiDeleteView(DeleteView):
    model = Boi
    template_name = 'boi/deletarboi.html'
    success_url = reverse_lazy('listaboi')

class BoiMorteView(UpdateView):
    model = Boi
    form_class = BoiMorteForm
    template_name = "boi/registrarmorte.html"
    success_url = reverse_lazy('listamorte')

class ListaBoiMorteView(ListView):
    model = Boi
    template_name = 'boi/listamorte.html'
    context_object_name = 'bois'

    def get_queryset(self):
        status_ids = StatusBoi.objects.filter(nome_status__in=['Ativo', 'Morto']).values_list('idstatus_boi', flat=True)

        queryset = super().get_queryset().filter(status_boi__in=status_ids).order_by('brinco')

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(brinco__icontains=search) |
                Q(fornecedor__nome_fornecedor__icontains=search) |
                Q(status_boi__nome_status__icontains=search) |
                Q(lote__nome_lote__icontains=search) |
                Q(data_entrada__icontains=search)
            ).order_by('brinco')

        return queryset