from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from app_financeiro import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # LOGIN
    path('', auth_views.LoginView.as_view(
        template_name='login/login.html'
    ), name='login'),

    path('login/', auth_views.LoginView.as_view(
        template_name='login/login.html'
    ), name='login'),

    # LOGOUT
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),

    # CLIENTES
    path('clientes/', views.clientes, name='clientes'),
]
