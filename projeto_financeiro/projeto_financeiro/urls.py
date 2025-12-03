from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app_financeiro import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Autenticação
    path('', auth_views.LoginView.as_view(
        template_name='login/login.html'
    ), name='login'),

    path('login/', auth_views.LoginView.as_view(
        template_name='login/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Clientes
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/atualizar/', views.cliente_atualizar, name='cliente_atualizar'),

    # Jobs
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/atualizar/', views.job_atualizar, name='job_atualizar'),

    # Cobranças
    path('cobrancas/', views.cobrancas, name='cobrancas'),
    path('cobrancas/atualizar/', views.cobranca_atualizar, name='cobranca_atualizar'),

    # Configurações
    path('configuracoes/', views.configuracoes, name='configuracoes'),

    # Notificações
    path('notificacoes/', views.notificacoes_list, name='notificacoes_list'),
    path('notificacoes/marcar-lidas/', views.notificacao_mark_all_read, name='notificacao_mark_all_read'),

    # Usuários (apenas para staff)
    path('usuarios/', views.usuarios, name='usuarios'),
    path('usuarios/<int:user_id>/toggle-active/', views.usuario_toggle_active, name='usuario_toggle_active'),
]