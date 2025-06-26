from django.shortcuts import render, redirect
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
from manejo.forms import ManejoForm, ParametroManejoFormSet, BoiEntradaFormSet, BuscaBoiForm,VendaBoiForm, ParametroMovimentacaoFormSet, MovimentacaoDataForm, ManejoUpdateForm, SaidaManejoForm
from manejo.models import Manejo, TipoManejo, StatusManejo, BoiManejo
from boi.models import StatusBoi
from boi.models import Boi, PesoMovimentacao
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
import datetime

def criar_manejo_entrada(request):
    template_name = 'manejo/manejoentrada.html'
    
    if request.method == 'POST':
        form_manejo = ManejoForm(request.POST)
        formset_parametros = ParametroManejoFormSet(request.POST, prefix='parametros')
        formset_bois = BoiEntradaFormSet(request.POST, prefix='bois')

        if form_manejo.is_valid() and formset_parametros.is_valid() and formset_bois.is_valid():
            
            # Use transaction.atomic para garantir a integridade dos dados
            try:
                with transaction.atomic():
                    # --- INÍCIO DA CORREÇÃO ---
                    # 1. Busque o TipoManejo "Entrada" antes de tudo
                    try:
                        tipo_entrada = TipoManejo.objects.get(nome_tipo_manejo__iexact='Entrada')
                    except TipoManejo.DoesNotExist:
                        messages.error(request, 'Erro Crítico: O tipo de manejo "Entrada" não existe no banco de dados.')
                        return redirect('listamanejo')

                    # 2. Crie o objeto em memória
                    manejo = form_manejo.save(commit=False)
                    
                    # 3. ATRIBUA OS VALORES QUE FALTAM
                    manejo.tipo_manejo = tipo_entrada # <-- PONTO PRINCIPAL DA CORREÇÃO
                    
                    # Você já estava fazendo isso corretamente para o status
                    status_concluido = StatusManejo.objects.get(nome_status_manejo='Concluido')
                    manejo.status_manejo = status_concluido
                    
                    # 4. Agora salve o manejo, pois ele está completo
                    manejo.save()
                    # --- FIM DA CORREÇÃO ---

                    formset_parametros.instance = manejo
                    formset_parametros.save()
                    
                    regras_deste_manejo = manejo.parametros_manejo.all()

                    status_ativo_boi = StatusBoi.objects.get(nome_status='Ativo')
                    bois_cadastrados = 0
                    for boi_form in formset_bois:
                        if boi_form.cleaned_data and not boi_form.cleaned_data.get('DELETE', False):
                            peso_entrada = boi_form.cleaned_data['peso_entrada']
                            raca_boi = boi_form.cleaned_data['raca']

                            lote_encontrado = None
                            for regra in regras_deste_manejo:
                                if regra.raca == raca_boi and regra.peso_inicial <= peso_entrada <= regra.peso_final:
                                    lote_encontrado = regra.lote
                                    break
                            
                            if not lote_encontrado:
                                # Esta exceção vai disparar o rollback da transação
                                raise ValueError(f"Nenhuma regra definida NESTE manejo para um boi da raça '{raca_boi}' com peso {peso_entrada}kg.")
                            
                            boi = boi_form.save(commit=False)
                            boi.lote = lote_encontrado
                            boi.status_boi = status_ativo_boi
                            boi.save()

                            BoiManejo.objects.create(boi=boi, manejo=manejo)
                            bois_cadastrados += 1
                    
                    if bois_cadastrados == 0:
                        raise ValueError("Nenhum boi foi adicionado ao manejo.")

                    messages.success(request, f"Manejo de entrada #{manejo.idManejo} criado com sucesso! {bois_cadastrados} boi(s) registrados.")
                    return redirect('listamanejo')

            except ValueError as e:
                # Captura o erro que levantamos manualmente para cancelar a transação
                messages.error(request, f"{e} A operação foi cancelada.")
                # Os formulários com os dados preenchidos serão renderizados novamente
            
            except Exception as e:
                # Captura qualquer outro erro inesperado
                messages.error(request, f"Ocorreu um erro inesperado: {e}. A operação foi cancelada.")


    else: 
        form_manejo = ManejoForm(initial={'tipo_manejo': TipoManejo.objects.filter(nome_tipo_manejo='Entrada').first()})
        formset_parametros = ParametroManejoFormSet(prefix='parametros')
        formset_bois = BoiEntradaFormSet(prefix='bois')

    context = {
        'form_manejo': form_manejo,
        'formset_parametros': formset_parametros,
        'formset_bois': formset_bois,
    }
    return render(request, template_name, context)




def manejo_saida_venda(request):
    template_name = 'manejo/manejosaida.html'
    context = {}

    # Garante que as variáveis de sessão existam
    if 'venda_atual' not in request.session:
        request.session['venda_atual'] = []
    if 'protocolo_saida_id' not in request.session:
        request.session['protocolo_saida_id'] = None

    # --- LÓGICA DO POST ---
    if request.method == 'POST':
        # Guarda o protocolo selecionado na sessão a cada ação POST
        protocolo_id_selecionado = request.POST.get('protocolo_sanitario')
        if protocolo_id_selecionado:
            request.session['protocolo_saida_id'] = protocolo_id_selecionado

        # --- AÇÃO: Finalizar a Venda ---
        if 'finalizar_venda' in request.POST:
            venda_atual = request.session.get('venda_atual', [])
            saida_manejo_form = SaidaManejoForm(request.POST)

            if not venda_atual:
                messages.error(request, "Não há animais na lista para vender.")
            elif saida_manejo_form.is_valid():
                try:
                    with transaction.atomic():
                        protocolo = saida_manejo_form.cleaned_data['protocolo_sanitario']
                        data_manejo_geral = datetime.datetime.strptime(venda_atual[0]['data_saida'], '%Y-%m-%d').date()

                        # CORREÇÃO 1: Usando __iexact para busca case-insensitive
                        tipo_manejo_saida = TipoManejo.objects.get(nome_tipo_manejo__iexact='saida')
                        status_concluido = StatusManejo.objects.get(nome_status_manejo__iexact='Concluido')

                        manejo = Manejo.objects.create(
                            tipo_manejo=tipo_manejo_saida,
                            status_manejo=status_concluido,
                            data_manejo=data_manejo_geral,
                            protocolo_sanitario=protocolo
                        )

                        status_vendido = StatusBoi.objects.get(nome_status='Vendido')
                        for boi_data in venda_atual:
                            boi = Boi.objects.get(pk=boi_data['boi_id'])
                            boi.peso_saida = boi_data['peso_saida']
                            boi.data_saida = datetime.datetime.strptime(boi_data['data_saida'], '%Y-%m-%d').date()
                            boi.status_boi = status_vendido
                            boi.save()
                            BoiManejo.objects.create(boi=boi, manejo=manejo)

                        # Limpa a sessão após o sucesso
                        del request.session['venda_atual']
                        del request.session['protocolo_saida_id']
                        messages.success(request, f"Venda de {len(venda_atual)} animais concluída com sucesso!")
                        return redirect('listamanejo')
                except TipoManejo.DoesNotExist:
                     messages.error(request, "Erro Crítico: O tipo de manejo 'saida' não existe no banco de dados.")
                except Exception as e:
                    messages.error(request, f"Ocorreu um erro ao finalizar a venda: {e}")
            else:
                 messages.error(request, "Erro de validação. Por favor, selecione um protocolo sanitário.")

        # --- AÇÃO: Remover Boi da Lista ---
        elif 'remover_da_venda' in request.POST:
            boi_id_remover = request.POST.get('remover_da_venda')
            if boi_id_remover:
                venda_atual = request.session.get('venda_atual', [])
                nova_lista = [b for b in venda_atual if b.get('boi_id') != int(boi_id_remover)]
                request.session['venda_atual'] = nova_lista
                request.session.modified = True
                messages.success(request, "Animal removido da lista de venda.")
            return redirect('manejo_saida_venda')

        # --- AÇÃO: Adicionar Boi à Lista ---
        elif 'adicionar_a_venda' in request.POST:
            venda_form = VendaBoiForm(request.POST)
            if venda_form.is_valid():
                boi_id = venda_form.cleaned_data['boi_id']
                venda_atual = request.session.get('venda_atual', [])
                if any(b['boi_id'] == boi_id for b in venda_atual):
                    messages.warning(request, "Este animal já está na lista de venda.")
                else:
                    nova_venda = {
                        'boi_id': boi_id, 'brinco': Boi.objects.get(pk=boi_id).brinco,
                        'peso_saida': str(venda_form.cleaned_data['peso_saida']),
                        'data_saida': venda_form.cleaned_data['data_saida'].strftime('%Y-%m-%d'),
                    }
                    venda_atual.append(nova_venda)
                    request.session['venda_atual'] = venda_atual
                    messages.success(request, f"Boi {nova_venda['brinco']} adicionado à venda.")
                return redirect('manejo_saida_venda')
            else:
                context['venda_form'] = venda_form
                context['boi_encontrado'] = Boi.objects.get(pk=request.POST.get('boi_id'))

        # --- AÇÃO: Buscar Boi ---
        elif 'buscar_boi' in request.POST:
            busca_form = BuscaBoiForm(request.POST)
            if busca_form.is_valid():
                brinco = busca_form.cleaned_data['brinco']
                try:
                    boi_encontrado = Boi.objects.get(brinco__iexact=brinco, status_boi__nome_status='Ativo')
                    context['boi_encontrado'] = boi_encontrado
                    context['venda_form'] = VendaBoiForm(initial={'boi_id': boi_encontrado.idboi, 'data_saida': datetime.date.today()})
                except Boi.DoesNotExist:
                    messages.error(request, f"Nenhum boi ATIVO encontrado com o brinco '{brinco}'.")
            context['busca_form'] = busca_form

    # --- LÓGICA DO GET (ou estado inicial) ---
    if 'busca_form' not in context:
        context['busca_form'] = BuscaBoiForm()
    
    # CORREÇÃO 2: Inicializa o formulário com o valor guardado na sessão
    protocolo_id_sessao = request.session.get('protocolo_saida_id')
    context['saida_manejo_form'] = SaidaManejoForm(initial={'protocolo_sanitario': protocolo_id_sessao})

    context['venda_atual'] = request.session.get('venda_atual', [])
    return render(request, template_name, context)




def manejo_movimentacao(request):
    template_name = 'manejo/manejomovimentacao.html'
    context = {}

    # Garante que a lista exista na sessão
    if 'movimentacao_atual' not in request.session:
        request.session['movimentacao_atual'] = []

    # --- LÓGICA DO POST ---
    if request.method == 'POST':
        # Instancia os formulários com os dados do POST para validação ou re-exibição
        manejo_form = ManejoForm(request.POST, prefix='manejo')
        formset_parametros = ParametroMovimentacaoFormSet(request.POST, prefix='parametros')
        busca_form = BuscaBoiForm(request.POST) # Instanciado aqui para o contexto
        
        # --- AÇÃO: Finalizar o Manejo ---
        if 'finalizar_movimentacao' in request.POST:
            animais_na_sessao = request.session.get('movimentacao_atual', [])
            
            if not animais_na_sessao:
                messages.error(request, "A lista de movimentação está vazia. Adicione animais antes de finalizar.")
            
            elif manejo_form.is_valid() and formset_parametros.is_valid():
                # Bloco de transação: ou tudo funciona, ou nada é salvo.
                try:
                    with transaction.atomic():
                        # 1. Preparar o objeto Manejo
                        tipo_mov = TipoManejo.objects.get(nome_tipo_manejo__iexact='movimentacao')
                        status_concluido = StatusManejo.objects.get(nome_status_manejo='Concluido')

                        manejo = manejo_form.save(commit=False)
                        manejo.tipo_manejo = tipo_mov
                        manejo.status_manejo = status_concluido
                        manejo.save()

                        # 2. Salvar os parâmetros (regras de lote)
                        formset_parametros.instance = manejo
                        formset_parametros.save()
                        regras_deste_manejo = manejo.parametros_manejo.all()

                        # 3. Processar cada animal da sessão
                        for dados_boi in animais_na_sessao:
                            boi = Boi.objects.select_related('lote', 'raca').get(pk=dados_boi['boi_id'])
                            novo_peso = Decimal(dados_boi['peso_movimentacao'])

                            PesoMovimentacao.objects.create(
                                boi=boi, peso_movimentacao=novo_peso, data_movimentacao=manejo.data_manejo
                            )
                            
                            novo_lote = None
                            for regra in regras_deste_manejo:
                                if regra.raca == boi.raca and regra.peso_inicial <= novo_peso <= regra.peso_final:
                                    novo_lote = regra.lote
                                    break
                            
                            if novo_lote is None:
                                raise ValueError(f"Nenhuma regra encontrada para o boi '{boi.brinco}' (Raça: {boi.raca.nome_raca}, Peso: {novo_peso}kg).")

                            if boi.lote != novo_lote:
                                boi.lote = novo_lote
                                boi.save(update_fields=['lote'])

                            BoiManejo.objects.create(boi=boi, manejo=manejo)

                        del request.session['movimentacao_atual']
                        messages.success(request, f"Manejo de movimentação #{manejo.idManejo} salvo com sucesso!")
                        return redirect('listamanejo')

                except (TipoManejo.DoesNotExist, StatusManejo.DoesNotExist):
                    messages.error(request, "Erro de configuração: Tipos ou Status de manejo essenciais ('movimentacao', 'Concluido') não foram encontrados no banco de dados. A operação foi cancelada.")
                except Boi.DoesNotExist:
                    messages.error(request, "Erro: um dos animais na lista não foi encontrado no banco de dados. A operação foi cancelada.")
                except ValueError as e: 
                    messages.error(request, f"{e} A operação foi cancelada.")
                except Exception as e: 
                    messages.error(request, f"Ocorreu um erro inesperado: {e}. A operação foi cancelada.")
            
            else:
                # --- MELHORIA: EXIBIÇÃO DETALHADA DE ERROS ---
                messages.error(request, "Não foi possível finalizar. Por favor, corrija os erros abaixo:")
                
                # Exibe erros do formulário principal de Manejo
                for field, errors in manejo_form.errors.items():
                    for error in errors:
                        messages.error(request, f"Campo '{manejo_form.fields[field].label}': {error}")
                
                # Exibe erros do formset de Parâmetros
                for i, form in enumerate(formset_parametros):
                    if form.errors:
                        messages.warning(request, f"Erros na Regra de Reclassificação #{i+1}:")
                        for field, errors in form.errors.items():
                            for error in errors:
                                # Acessa o 'label' do campo para uma mensagem mais amigável
                                label = form.fields.get(field).label if form.fields.get(field) else field
                                messages.error(request, f"- Campo '{label}': {error}")

        # --- AÇÃO: Adicionar Boi à Lista ---
        elif 'adicionar_boi' in request.POST:
            mov_data_form = MovimentacaoDataForm(request.POST)
            if mov_data_form.is_valid():
                boi_id = mov_data_form.cleaned_data['boi_id']
                if not any(b['boi_id'] == boi_id for b in request.session['movimentacao_atual']):
                    boi_instance = Boi.objects.get(pk=boi_id)
                    request.session['movimentacao_atual'].append({
                        'boi_id': boi_id,
                        'brinco': boi_instance.brinco,
                        'lote_atual': boi_instance.lote.nome_lote if boi_instance.lote else 'Sem Lote',
                        'peso_movimentacao': str(mov_data_form.cleaned_data['peso_movimentacao'])
                    })
                    request.session.modified = True
                    messages.success(request, f"Boi {boi_instance.brinco} adicionado à lista.")
                else:
                    messages.warning(request, "Este animal já está na lista.")
                return redirect('manejo_movimentacao')
            else:
                context['mov_data_form'] = mov_data_form
                context['boi_encontrado'] = Boi.objects.get(pk=request.POST.get('boi_id'))

        # --- AÇÃO: Buscar Boi ---
        elif 'buscar_boi' in request.POST:
            if busca_form.is_valid():
                brinco = busca_form.cleaned_data['brinco']
                try:
                    status_ativo = StatusBoi.objects.get(nome_status__iexact='Ativo')
                    boi_encontrado = Boi.objects.get(brinco__iexact=brinco, status_boi=status_ativo)
                    context['boi_encontrado'] = boi_encontrado
                    context['mov_data_form'] = MovimentacaoDataForm(initial={'boi_id': boi_encontrado.idboi})
                except (Boi.DoesNotExist, StatusBoi.DoesNotExist):
                    messages.error(request, f"Nenhum boi ATIVO encontrado com o brinco '{brinco}'.")
        
        elif 'remover_boi' in request.POST:
            boi_id_remover = request.POST.get('remover_boi')
            if boi_id_remover:
                animais_na_sessao = request.session.get('movimentacao_atual', [])
                
                # Cria uma nova lista sem o boi que corresponde ao ID a ser removido
                nova_lista = [b for b in animais_na_sessao if b.get('boi_id') != int(boi_id_remover)]
                
                # Atualiza a sessão com a nova lista
                request.session['movimentacao_atual'] = nova_lista
                request.session.modified = True
                messages.success(request, "Animal removido da lista de movimentação.")

            return redirect('manejo_movimentacao')
        
        context['manejo_form'] = manejo_form
        context['formset_parametros'] = formset_parametros
        context['busca_form'] = busca_form

    # --- LÓGICA DO GET (ou estado inicial) ---
    else:
        context['manejo_form'] = ManejoForm(prefix='manejo', initial={'data_manejo': datetime.date.today()})
        context['formset_parametros'] = ParametroMovimentacaoFormSet(prefix='parametros')
        context['busca_form'] = BuscaBoiForm()

    context['animais_na_movimentacao'] = request.session.get('movimentacao_atual', [])
    
    return render(request, template_name, context)





class ManejoListView(ListView):
    model = Manejo
    template_name = 'manejo/listamanejo.html'
    context_object_name = 'manejos'
    

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'tipo_manejo', 'status_manejo', 'protocolo_sanitario'
        ).order_by('-data_manejo', '-idManejo')

        
        tipo_manejo_str = self.kwargs.get('tipo')
        if tipo_manejo_str:
            queryset = queryset.filter(tipo_manejo__nome_tipo_manejo__iexact=tipo_manejo_str)

      
        search_query = self.request.GET.get('q')  
        if search_query:

            query_filter = Q(protocolo_sanitario__nome_protocolo__icontains=search_query)
            if search_query.isdigit():
                query_filter |= Q(idManejo=int(search_query))
            
            queryset = queryset.filter(query_filter)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        

        tipo_filtro = self.kwargs.get('tipo')
        
        context['tipo_filtro'] = tipo_filtro if tipo_filtro else 'Todos'
        context['search_query'] = self.request.GET.get('q', '')

        url_map = {
            'entrada': 'criar_manejo_entrada',
            'saida': 'manejo_saida_venda',
            'movimentacao': 'manejo_movimentacao',
        }
        

        context['url_adicionar'] = url_map.get(tipo_filtro, 'criar_manejo_entrada')
  
        return context
    
class ManejoDetailView(DetailView):
    model = Manejo
    template_name = 'manejo/detalhemanejo.html'
    context_object_name = 'manejo'

class ManejoUpdateView(UpdateView):
    model = Manejo
    form_class = ManejoUpdateForm
    template_name = 'manejo/atualizarmanejo.html'
    context_object_name = 'manejo'
    success_url = reverse_lazy('listamanejo')