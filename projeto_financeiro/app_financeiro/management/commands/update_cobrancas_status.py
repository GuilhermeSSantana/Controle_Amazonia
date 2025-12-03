"""
Comando para atualizar status de cobranças automaticamente
Crie em: app_financeiro/management/commands/update_cobrancas_status.py
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from app_financeiro.models import Cobranca, Notification
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Atualiza o status das cobranças baseado na data de vencimento'

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        
        # Atualizar cobranças vencidas
        cobrancas_vencidas = Cobranca.objects.filter(
            status='pendente',
            due_date__lt=today
        )
        
        count_vencidas = cobrancas_vencidas.count()
        cobrancas_vencidas.update(status='vencida')
        
        # Criar notificações para cobranças vencidas
        if count_vencidas > 0:
            # Notificar todos os usuários staff
            staff_users = User.objects.filter(is_staff=True, is_active=True)
            
            for user in staff_users:
                Notification.objects.create(
                    user=user,
                    type='cobranca_vencida',
                    title=f'{count_vencidas} cobrança(s) vencida(s)',
                    message=f'Existem {count_vencidas} cobrança(s) que venceram e precisam de atenção.',
                    link='/cobrancas/?status=vencida'
                )
        
        # Notificar sobre cobranças que vencem em 3 dias
        tres_dias = today + timezone.timedelta(days=3)
        cobrancas_vencendo = Cobranca.objects.filter(
            status='pendente',
            due_date=tres_dias
        )
        
        count_vencendo = cobrancas_vencendo.count()
        
        if count_vencendo > 0:
            staff_users = User.objects.filter(is_staff=True, is_active=True)
            
            for user in staff_users:
                Notification.objects.create(
                    user=user,
                    type='cobranca_vencendo',
                    title=f'{count_vencendo} cobrança(s) vencendo em 3 dias',
                    message=f'Existem {count_vencendo} cobrança(s) que vencem em 3 dias.',
                    link='/cobrancas/?status=pendente'
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Status atualizado: {count_vencidas} vencidas, {count_vencendo} vencendo em breve'
            )
        )