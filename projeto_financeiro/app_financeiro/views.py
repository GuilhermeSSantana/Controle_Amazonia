from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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

    # Filtros e busca
    q = (request.GET.get("q") or "").strip()
    status = request.GET.get("status") or "todos"

    base_qs = Client.objects.all()
    total_count = base_qs.count()
    active_count = base_qs.filter(is_active=True).count()
    inactive_count = base_qs.filter(is_active=False).count()

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

    context = {
        "page_title": "Clientes",
        "page_subtitle": "Gerencie sua base de clientes",
        "form": ClientForm(),  # formulário em branco na tela
        "clients": clients.order_by("name"),
        "total_count": total_count,
        "active_count": active_count,
        "inactive_count": inactive_count,
    }
    return render(request, "clientes/clientes.html", context)


@login_required
def cliente_detalhe(request, pk):
    client = get_object_or_404(Client, pk=pk)
    context = {
        "client": client,
        "page_title": f"Cliente - {client.name}",
    }
    return render(request, "clientes/cliente_detalhe.html", context)


@login_required
@require_POST
def cliente_atualizar(request):
    client_id = request.POST.get("client_id")
    client = get_object_or_404(Client, pk=client_id)

    # ✅ AGORA SALVA O NOME TAMBÉM
    client.name = (request.POST.get("name") or "").strip()
    client.email = (request.POST.get("email") or "").strip()
    client.phone = (request.POST.get("phone") or "").strip()
    client.address = (request.POST.get("address") or "").strip()
    client.notes = (request.POST.get("notes") or "").strip()
    client.is_active = bool(request.POST.get("is_active"))

    client.save()

    return redirect("clientes")