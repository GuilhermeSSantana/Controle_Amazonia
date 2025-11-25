from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Client
from .forms import ClientForm


@login_required
def dashboard(request):
    context = {
        'page_title': 'Dashboard',
        'page_subtitle': 'Visão geral do seu negócio',
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def clientes(request):
    # Cadastro via POST
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("clientes")
    else:
        form = ClientForm()

    # --- Filtros e busca ---
    q = (request.GET.get("q") or "").strip()
    status = request.GET.get("status") or "todos"

    # Base para contar
    base_qs = Client.objects.all()

    total_count = base_qs.count()
    active_count = base_qs.filter(is_active=True).count()
    inactive_count = base_qs.filter(is_active=False).count()

    # Query que será exibida
    clients = base_qs

    if q:
        clients = clients.filter(
            Q(name__icontains=q)
            | Q(document__icontains=q)
            | Q(email__icontains=q)
        )

    if status == "ativo":
        clients = clients.filter(is_active=True)
    elif status == "inativo":
        clients = clients.filter(is_active=False)
    # se for "todos", não filtra por status

    context = {
        "page_title": "Clientes",
        "page_subtitle": "Gerencie sua base de clientes",
        "form": form,
        "clients": clients.order_by("name"),
        "total_count": total_count,
        "active_count": active_count,
        "inactive_count": inactive_count,
    }
    return render(request, "clientes/clientes.html", context)
