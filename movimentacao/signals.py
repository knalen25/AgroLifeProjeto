from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movimentacao
from boi.models import Boi
from movimentacao.models import StatusMovimentacao

@receiver(post_save, sender=Movimentacao)
def atualizar_animais_e_curral(sender, instance, created, **kwargs):
    if created:

        lote_destino = instance.lote_destino
        lote_destino.curral = instance.curral_destino
        lote_destino.save()

        Boi.objects.filter(lote=instance.lote_origem).update(lote=instance.lote_destino)



# @receiver(post_save, sender=Movimentacao)
# def executar_movimentacao_quando_fechada(sender, instance, created, **kwargs):

#     if not created:
#         try:
         
#             status_fechado = StatusMovimentacao.objects.get(nome_status__iexact='Fechado')

    
#             if instance.status == status_fechado:
                
    
#                 lote_destino = instance.lote_destino
#                 lote_destino.curral = instance.curral_destino
#                 lote_destino.save(update_fields=['curral'])

             
#                 if instance.lote_origem != instance.lote_destino:
#                     Boi.objects.filter(lote=instance.lote_origem).update(lote=lote_destino)
        
#         except StatusMovimentacao.DoesNotExist:

#             pass