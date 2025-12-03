#!/usr/bin/env python
"""
Script de atualização automática do sistema
Execute: python setup_update.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projeto_financeiro.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth.models import User
from app_financeiro.models import SystemConfig, Cobranca, Notification

def print_header(text):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"✅ {text}")

def print_error(text):
    """Imprime mensagem de erro"""
    print(f"❌ {text}")

def print_info(text):
    """Imprime mensagem informativa"""
    print(f"ℹ️  {text}")

def create_system_config():
    """Cria configuração inicial do sistema"""
    print_header("Criando Configuração do Sistema")
    
    try:
        config = SystemConfig.get_config()
        print_success(f"Configuração criada/recuperada: {config.company_name}")
        print_info(f"   CNPJ: {config.company_cnpj}")
        print_info(f"   Email: {config.company_email}")
        return True
    except Exception as e:
        print_error(f"Erro ao criar configuração: {e}")
        return False

def update_cobrancas_status():
    """Atualiza status das cobranças vencidas"""
    print_header("Atualizando Status das Cobranças")
    
    try:
        today = timezone.localdate()
        updated = Cobranca.objects.filter(
            status='pendente',
            due_date__lt=today
        ).update(status='vencida')
        
        print_success(f"{updated} cobrança(s) marcada(s) como vencida(s)")
        return True
    except Exception as e:
        print_error(f"Erro ao atualizar cobranças: {e}")
        return False

def create_initial_notifications():
    """Cria notificações iniciais para cobranças"""
    print_header("Criando Notificações Iniciais")
    
    try:
        # Pegar o primeiro usuário admin
        admin_users = User.objects.filter(is_superuser=True)
        if not admin_users.exists():
            print_error("Nenhum usuário admin encontrado!")
            return False
        
        admin = admin_users.first()
        today = timezone.localdate()
        created = 0
        
        # Notificações para cobranças vencidas
        cobrancas_vencidas = Cobranca.objects.filter(status='vencida')
        for cobranca in cobrancas_vencidas:
            # Verifica se já existe notificação
            if not Notification.objects.filter(
                user=admin,
                type='cobranca_vencida',
                message__icontains=cobranca.number
            ).exists():
                Notification.objects.create(
                    user=admin,
                    type='cobranca_vencida',
                    title=f'Cobrança #{cobranca.number} vencida',
                    message=f'Cobrança de {cobranca.client.name} no valor de R$ {cobranca.value} venceu em {cobranca.due_date.strftime("%d/%m/%Y")}',
                    link=f'/cobrancas/?q={cobranca.number}'
                )
                created += 1
        
        # Notificações para cobranças vencendo (próximos 3 dias)
        from datetime import timedelta
        tres_dias = today + timedelta(days=3)
        cobrancas_vencendo = Cobranca.objects.filter(
            status='pendente',
            due_date__gte=today,
            due_date__lte=tres_dias
        )
        
        for cobranca in cobrancas_vencendo:
            if not Notification.objects.filter(
                user=admin,
                type='cobranca_vencendo',
                message__icontains=cobranca.number
            ).exists():
                dias = (cobranca.due_date - today).days
                Notification.objects.create(
                    user=admin,
                    type='cobranca_vencendo',
                    title=f'Cobrança #{cobranca.number} vence em {dias} dia(s)',
                    message=f'Cobrança de {cobranca.client.name} no valor de R$ {cobranca.value} vence em {cobranca.due_date.strftime("%d/%m/%Y")}',
                    link=f'/cobrancas/?q={cobranca.number}'
                )
                created += 1
        
        print_success(f"{created} notificação(ões) criada(s)")
        return True
    except Exception as e:
        print_error(f"Erro ao criar notificações: {e}")
        return False

def show_statistics():
    """Mostra estatísticas do sistema"""
    print_header("Estatísticas do Sistema")
    
    try:
        from app_financeiro.models import Client, Job
        from decimal import Decimal
        from django.db.models import Sum, Q
        
        total_clientes = Client.objects.count()
        clientes_ativos = Client.objects.filter(is_active=True).count()
        
        total_jobs = Job.objects.count()
        jobs_ativos = Job.objects.filter(status__in=['pendente', 'em_andamento']).count()
        
        total_cobrancas = Cobranca.objects.count()
        cobrancas_pagas = Cobranca.objects.filter(status='paga').count()
        cobrancas_vencidas = Cobranca.objects.filter(status='vencida').count()
        
        valor_total = Cobranca.objects.aggregate(total=Sum('value'))['total'] or Decimal('0')
        valor_pago = Cobranca.objects.filter(status='paga').aggregate(total=Sum('value'))['total'] or Decimal('0')
        
        print_info(f"📊 Clientes: {total_clientes} total ({clientes_ativos} ativos)")
        print_info(f"💼 Jobs: {total_jobs} total ({jobs_ativos} ativos)")
        print_info(f"💰 Cobranças: {total_cobrancas} total")
        print_info(f"   ├─ Pagas: {cobrancas_pagas}")
        print_info(f"   └─ Vencidas: {cobrancas_vencidas}")
        print_info(f"💵 Valor Total: R$ {valor_total:.2f}")
        print_info(f"✅ Valor Recebido: R$ {valor_pago:.2f}")
        
        return True
    except Exception as e:
        print_error(f"Erro ao obter estatísticas: {e}")
        return False

def verify_context_processor():
    """Verifica se o context processor está configurado"""
    print_header("Verificando Configurações")
    
    try:
        from django.conf import settings
        
        context_processors = []
        for template in settings.TEMPLATES:
            if 'OPTIONS' in template and 'context_processors' in template['OPTIONS']:
                context_processors = template['OPTIONS']['context_processors']
                break
        
        target = 'app_financeiro.context_processors.notifications_processor'
        if target in context_processors:
            print_success("Context processor configurado corretamente!")
        else:
            print_error("Context processor NÃO configurado!")
            print_info("Adicione esta linha ao TEMPLATES no settings.py:")
            print_info(f"   '{target}'")
            return False
        
        return True
    except Exception as e:
        print_error(f"Erro ao verificar configurações: {e}")
        return False

def main():
    """Função principal"""
    print("\n")
    print("🚀 " + "="*56)
    print("   SCRIPT DE ATUALIZAÇÃO DO SISTEMA FINANCEIRO")
    print("="*60)
    
    # Executar etapas
    steps = [
        ("Verificando configurações", verify_context_processor),
        ("Criando configuração do sistema", create_system_config),
        ("Atualizando status das cobranças", update_cobrancas_status),
        ("Criando notificações iniciais", create_initial_notifications),
        ("Exibindo estatísticas", show_statistics),
    ]
    
    results = []
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
        except Exception as e:
            print_error(f"Erro em '{step_name}': {e}")
            results.append((step_name, False))
    
    # Resumo final
    print_header("Resumo da Atualização")
    
    success_count = sum(1 for _, result in results if result)
    total_count = len(results)
    
    for step_name, result in results:
        status = "✅ OK" if result else "❌ ERRO"
        print(f"{status} - {step_name}")
    
    print("\n" + "="*60)
    print(f"   {success_count}/{total_count} etapas concluídas com sucesso")
    print("="*60 + "\n")
    
    if success_count == total_count:
        print("🎉 Sistema atualizado com sucesso!")
        print("\nPróximos passos:")
        print("1. Acesse /dashboard/ para ver as métricas")
        print("2. Clique no sino 🔔 para ver notificações")
        print("3. Acesse /configuracoes/ para editar configurações")
        print("4. Acesse /usuarios/ para gerenciar usuários")
    else:
        print("⚠️  Algumas etapas falharam. Verifique os erros acima.")
    
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Atualização cancelada pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Erro fatal: {e}")
        sys.exit(1)