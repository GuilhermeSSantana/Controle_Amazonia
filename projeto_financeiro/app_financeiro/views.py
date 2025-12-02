from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Client, Job, Cobranca
from .forms import ClientForm, JobForm, CobrancaForm


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
            messages.success(request, "Cliente cadastrado com sucesso!")
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
        "form": ClientForm(),
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

    client.name = (request.POST.get("name") or "").strip()
    client.email = (request.POST.get("email") or "").strip()
    client.phone = (request.POST.get("phone") or "").strip()
    client.address = (request.POST.get("address") or "").strip()
    client.notes = (request.POST.get("notes") or "").strip()
    client.is_active = bool(request.POST.get("is_active"))

    client.save()
    messages.success(request, "Cliente atualizado com sucesso!")
    return redirect("clientes")


@login_required
def jobs(request):
    """
    Lista jobs + faz cadastro via modal (POST).
    """
    # Cadastro via POST
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Job cadastrado com sucesso!")
            return redirect("jobs")
    else:
        form = JobForm()

    # Filtros e busca
    q = (request.GET.get("q") or "").strip()
    status = request.GET.get("status") or "todos"

    base_qs = Job.objects.select_related("client").all()

    if q:
        base_qs = base_qs.filter(
            Q(title__icontains=q)
            | Q(description__icontains=q)
            | Q(client__name__icontains=q)
        )

    if status in ["pendente", "em_andamento", "concluido"]:
        base_qs = base_qs.filter(status=status)

    jobs_qs = base_qs.order_by("-start_date", "title")

    # Contadores
    total_count = Job.objects.count()
    andamento_count = Job.objects.filter(status="em_andamento").count()
    concluido_count = Job.objects.filter(status="concluido").count()
    pendente_count = Job.objects.filter(status="pendente").count()

    # ✅ CÁLCULO DO VALOR TOTAL
    valor_total = Job.objects.aggregate(total=Sum('value'))['total'] or Decimal('0.00')

    # Para usar no select do modal de edição
    clients = Client.objects.filter(is_active=True).order_by("name")

    context = {
        "page_title": "Jobs",
        "page_subtitle": "Gerencie seus projetos e serviços",
        "form": form,
        "jobs": jobs_qs,
        "total_count": total_count,
        "andamento_count": andamento_count,
        "concluido_count": concluido_count,
        "pendente_count": pendente_count,
        "valor_total": valor_total,
        "search_query": q,
        "current_status": status,
        "clients": clients,
    }
    return render(request, "jobs/jobs.html", context)


@login_required
@require_POST
def job_atualizar(request):
    job_id = request.POST.get("job_id")
    job = get_object_or_404(Job, pk=job_id)

    # Campos texto
    job.title = (request.POST.get("title") or "").strip()
    job.status = (request.POST.get("status") or "pendente").strip()
    job.description = (request.POST.get("description") or "").strip()

    # Cliente relacional (vem um ID do select)
    client_id = request.POST.get("client_id") or request.POST.get("client")
    if client_id:
        job.client_id = int(client_id)

    # Datas (YYYY-MM-DD)
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
        normalized = value_raw.replace(".", "").replace(",", ".")
        try:
            job.value = Decimal(normalized)
        except InvalidOperation:
            messages.error(
                request,
                "O valor deve ser um número válido. Ex: 230,00 ou 230.00.",
            )
            return redirect("jobs")

    job.save()
    messages.success(request, "Job atualizado com sucesso!")
    return redirect("jobs")


@login_required
def cobrancas(request):
    """
    Lista cobranças + filtros + cadastro via modal.
    """
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "todos")

    cobrancas_qs = Cobranca.objects.select_related("client", "job")

    if q:
        cobrancas_qs = cobrancas_qs.filter(
            Q(number__icontains=q)
            | Q(client__name__icontains=q)
            | Q(job__title__icontains=q)
        )

    if status in ("pendente", "paga", "vencida"):
        cobrancas_qs = cobrancas_qs.filter(status=status)

    total_count = Cobranca.objects.count()
    pendente_count = Cobranca.objects.filter(status="pendente").count()
    paga_count = Cobranca.objects.filter(status="paga").count()
    vencida_count = Cobranca.objects.filter(status="vencida").count()

    totals = Cobranca.objects.aggregate(
        total_value=Sum("value"),
        paid_value=Sum("value", filter=Q(status="paga")),
        overdue_value=Sum("value", filter=Q(status="vencida")),
    )
    total_value = totals["total_value"] or Decimal("0")
    paid_value = totals["paid_value"] or Decimal("0")
    overdue_value = totals["overdue_value"] or Decimal("0")
    to_receive_value = total_value - paid_value

    # cadastro (POST)
    if request.method == "POST":
        form = CobrancaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cobrança cadastrada com sucesso.")
            return redirect("cobrancas")
    else:
        form = CobrancaForm()

    # ✅ Para os selects dos modais
    clients = Client.objects.order_by("name")
    jobs = Job.objects.select_related("client").order_by("title")

    context = {
        "page_title": "Cobranças",
        "page_subtitle": "Gerencie suas faturas e recebimentos",
        "cobrancas": cobrancas_qs,
        "search_query": q,
        "current_status": status,
        "total_count": total_count,
        "pendente_count": pendente_count,
        "paga_count": paga_count,
        "vencida_count": vencida_count,
        "total_value": total_value,
        "paid_value": paid_value,
        "to_receive_value": to_receive_value,
        "overdue_value": overdue_value,
        "form": form,
        "clients": clients,
        "jobs": jobs,  # ✅ ADICIONADO
    }
    return render(request, "cobrancas/cobrancas.html", context)


@login_required
@require_POST
def cobranca_atualizar(request):
    """
    Atualiza cobrança via modal de edição.
    """
    cobranca_id = request.POST.get("cobranca_id")
    cobranca = get_object_or_404(Cobranca, pk=cobranca_id)

    # Cliente
    client_id = request.POST.get("client_id")
    if client_id:
        try:
            cobranca.client = Client.objects.get(pk=client_id)
        except Client.DoesNotExist:
            messages.error(request, "Cliente inválido.")
            return redirect("cobrancas")

    # Job (opcional)
    job_id = request.POST.get("job_id")
    if job_id:
        try:
            cobranca.job = Job.objects.get(pk=job_id)
        except Job.DoesNotExist:
            cobranca.job = None
    else:
        cobranca.job = None

    # Número
    number = request.POST.get("number")
    if number:
        cobranca.number = number

    # Valor – trata vírgula/ponto
    raw_value = request.POST.get("value")
    if raw_value:
        cleaned = (
            raw_value.replace("R$", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", ".")
        )
        try:
            cobranca.value = Decimal(cleaned)
        except (InvalidOperation, ValueError):
            messages.error(request, "Valor inválido.")
            return redirect("cobrancas")

    # Datas
    issue_date = request.POST.get("issue_date")
    if issue_date:
        cobranca.issue_date = issue_date

    due_date = request.POST.get("due_date")
    if due_date:
        cobranca.due_date = due_date

    payment_date = request.POST.get("payment_date")
    if payment_date:
        cobranca.payment_date = payment_date
    else:
        cobranca.payment_date = None

    # Status
    status = request.POST.get("status")
    if status in ("pendente", "vencida", "paga"):
        cobranca.status = status

    # Observações
    cobranca.notes = request.POST.get("notes", "")

    cobranca.save()
    messages.success(request, "Cobrança atualizada com sucesso.")
    return redirect("cobrancas")