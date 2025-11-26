from django.shortcuts import render, redirect, get_object_or_404
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
def cliente_editar(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect("cliente_detalhe", pk=client.pk)
    else:
        form = ClientForm(instance=client)

    context = {
        "client": client,
        "form": form,
        "page_title": f"Editar Cliente - {client.name}",
        "is_edit": True,
    }
    return render(request, "clientes/cliente_editar.html", context)


@login_required
def cliente_excluir(request, pk):
    client = get_object_or_404(Client, pk=pk)

    if request.method == "POST":
        client.delete()
        return redirect("clientes")

    context = {
        "client": client,
        "page_title": f"Excluir Cliente - {client.name}",
    }
    return render(request, "clientes/cliente_excluir.html", context)
