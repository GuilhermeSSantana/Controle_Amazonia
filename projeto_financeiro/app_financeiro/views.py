from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from decimal import Decimal, InvalidOperation

from .models import Client
from .forms import ClientForm
from .models import Job
from .forms import JobForm

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

@login_required
def jobs(request):
    # Cadastro via POST (modal de "Novo Job")
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("jobs")
    else:
        form = JobForm()

    # Filtros e busca
    q = (request.GET.get("q") or "").strip()
    status = request.GET.get("status") or "todos"

    base_qs = Job.objects.all()

    total_count = base_qs.count()
    andamento_count = base_qs.filter(status="em_andamento").count()
    concluido_count = base_qs.filter(status="concluido").count()
    pendente_count = base_qs.filter(status="pendente").count()

    jobs_qs = base_qs

    if q:
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=q)
            | Q(client__icontains=q)
            | Q(description__icontains=q)
        )

    if status in ["pendente", "em_andamento", "concluido"]:
        jobs_qs = jobs_qs.filter(status=status)

    context = {
        "page_title": "Jobs & Serviços",
        "page_subtitle": "Gerencie seus projetos e serviços",
        "active_menu": "jobs",  # pra sidebar marcar o menu correto
        "form": form,
        "jobs": jobs_qs.order_by("delivery_date"),
        "total_count": total_count,
        "andamento_count": andamento_count,
        "concluido_count": concluido_count,
        "pendente_count": pendente_count,
        "current_status": status,
        "search_query": q,
    }
    return render(request, "jobs/jobs.html", context)


@login_required
def job_detalhe(request, pk):
    job = get_object_or_404(Job, pk=pk)
    context = {
        "job": job,
        "page_title": f"Job - {job.title}",
    }
    return render(request, "jobs/job_detalhe.html", context)


@login_required
@require_POST
def job_atualizar(request):
    job_id = request.POST.get("job_id")
    job = get_object_or_404(Job, pk=job_id)

    # Campos texto
    job.title = (request.POST.get("title") or "").strip()
    job.client = (request.POST.get("client") or "").strip()
    job.status = (request.POST.get("status") or "pendente").strip()
    job.description = (request.POST.get("description") or "").strip()

    # Datas (input type="date" já manda no formato YYYY-MM-DD)
    start_date_raw = request.POST.get("start_date") or None
    delivery_date_raw = request.POST.get("delivery_date") or None
    job.start_date = start_date_raw or None
    job.delivery_date = delivery_date_raw or None

    # Progresso
    progress_raw = request.POST.get("progress") or "0"
    try:
        job.progress = int(progress_raw)
    except ValueError:
        job.progress = 0

    # Valor – normalizar "1.230,50" / "230,00" / "230.00"
    value_raw = (request.POST.get("value") or "").strip()
    if value_raw:
        # remove separador de milhar e converte vírgula decimal para ponto
        normalized = value_raw.replace('.', '').replace(',', '.')
        try:
            job.value = Decimal(normalized)
        except InvalidOperation:
            messages.error(
                request,
                "O valor deve ser um número válido. Ex: 230,00 ou 230.00."
            )
            return redirect("jobs")

    job.save()
    return redirect("jobs")