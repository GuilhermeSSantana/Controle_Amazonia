from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app_financeiro.views import dashboard
from app_financeiro import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', auth_views.LoginView.as_view(
        template_name='login/login.html'
    ), name='login'),

    path('login/', auth_views.LoginView.as_view(
        template_name='login/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('dashboard/', dashboard, name='dashboard'),

    # CLIENTES – listagem + cadastro
    path("clientes/", views.clientes, name="clientes"),

    # CLIENTES – atualização via modal de detalhes
    path("clientes/atualizar/", views.cliente_atualizar, name="cliente_atualizar"),
]