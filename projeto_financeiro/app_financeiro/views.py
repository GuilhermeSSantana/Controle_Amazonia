from decimal import Decimal, InvalidOperation
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Client, Job, Cobranca, Notification, SystemConfig
from .forms import ClientForm, JobForm, CobrancaForm, SystemConfigForm, UserCreateForm


def get_base_context(request):
    """Contexto base para todas as páginas"""
    context = {}
    
    if request.user.is_authenticated:
        # Notificações não lidas
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )
        context['unread_count'] = unread_notifications.count()
        context['recent_notifications'] = Notification.objects.filter(
            user=request.user
        )[:5]
    
    return context


@login_required
def dashboard(request):
    """Dashboard principal com métricas e resumos"""
    today = timezone.localdate()
    
    # Métricas básicas
    total_clientes = Client.objects.filter(is_active=True).count()
    jobs_ativos = Job.objects.filter(status__in=['pendente', 'em_andamento']).count()
    
    # Faturamento mensal (cobranças pagas no mês atual)
    faturamento_mensal = Cobranca.objects.filter(
        status='paga',
        payment_date__year=today.year,
        payment_date__month=today.month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    
    # Faturamento mês anterior (para calcular crescimento)
    mes_anterior = today.replace(day=1) - timedelta(days=1)
    faturamento_mes_anterior = Cobranca.objects.filter(
        status='paga',
        payment_date__year=mes_anterior.year,
        payment_date__month=mes_anterior.month
    ).aggregate(total=Sum('value'))['total'] or Decimal('0.00')
    
    # Cálculo de crescimento
    crescimento = 0
    if faturamento_mes_anterior > 0:
        crescimento = ((faturamento_mensal - faturamento_mes_anterior) / faturamento_mes_anterior) * 100
    
    # Cobranças vencidas
    cobrancas_vencidas = Cobranca.objects.filter(
        status='vencida'
    ).count()
    
    # Resumo semanal
    semana_inicio = today
    semana_fim = today + timedelta(days=7)
    
    vencem_semana = Cobranca.objects.filter(
        due_date__gte=semana_inicio,
        due_date__lte=semana_fim,
        status='pendente'
    ).count()
    
    vencidas = Cobranca.objects.filter(status='vencida').count()
    em_dia = Cobranca.objects.filter(status='paga').count()
    
    # Cobranças recentes
    cobrancas_recentes = Cobranca.objects.select_related(
        'client', 'job'
    ).order_by('-created_at')[:5]
    
    context = get_base_context(request)
    context.update({
        'page_title': 'Dashboard',
        'total_clientes': total_clientes,
        'jobs_ativos': jobs_ativos,
        'faturamento_mensal': faturamento_mensal,
        'crescimento': round(crescimento, 2),
        'cobrancas_vencidas': cobrancas_vencidas,
        'vencem_semana': vencem_semana,
        'vencidas': vencidas,
        'em_dia': em_dia,
        'cobrancas_recentes': cobrancas_recentes,
    })
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def clientes(request):
    """Lista e cadastra clientes"""
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cliente cadastrado com sucesso!")
                return redirect("clientes")
            except Exception as e:
                messages.error(request, f"Erro ao cadastrar cliente: {str(e)}")
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

    context = get_base_context(request)
    context.update({
        "page_title": "Clientes",
        "form": form,
        "clients": clients.order_by("name"),
        "total_count": total_count,
        "active_count": active_count,
        "inactive_count": inactive_count,
    })
    
    return render(request, "clientes/clientes.html", context)


@login_required
@require_POST
def cliente_atualizar(request):
    """Atualiza dados do cliente"""
    client_id = request.POST.get("client_id")
    client = get_object_or_404(Client, pk=client_id)

    client.name = (request.POST.get("name") or "").strip()
    client.email = (request.POST.get("email") or "").strip() or None
    client.phone = (request.POST.get("phone") or "").strip() or None
    client.address = (request.POST.get("address") or "").strip()
    client.notes = (request.POST.get("notes") or "").strip()
    client.is_active = bool(request.POST.get("is_active"))

    try:
        client.save()
        messages.success(request, "Cliente atualizado com sucesso!")
    except Exception as e:
        messages.error(request, f"Erro ao atualizar cliente: {str(e)}")
    
    return redirect("clientes")


@login_required
def jobs(request):
    """Lista e cadastra jobs"""
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
    valor_total = Job.objects.aggregate(total=Sum('value'))['total'] or Decimal('0.00')

    clients = Client.objects.filter(is_active=True).order_by("name")

    context = get_base_context(request)
    context.update({
        "page_title": "Jobs",
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
    })
    
    return render(request, "jobs/jobs.html", context)


@login_required
@require_POST
def job_atualizar(request):
    """Atualiza job existente"""
    job_id = request.POST.get("job_id")
    job = get_object_or_404(Job, pk=job_id)

    job.title = (request.POST.get("title") or "").strip()
    job.status = (request.POST.get("status") or "pendente").strip()
    job.description = (request.POST.get("description") or "").strip()

    client_id = request.POST.get("client_id") or request.POST.get("client")
    if client_id:
        job.client_id = int(client_id)

    start_date_raw = request.POST.get("start_date")
    if start_date_raw:
        job.start_date = start_date_raw

    delivery_date_raw = request.POST.get("delivery_date")
    if delivery_date_raw:
        job.delivery_date = delivery_date_raw

    progress_raw = request.POST.get("progress") or "0"
    try:
        job.progress = int(progress_raw)
    except ValueError:
        job.progress = 0

    value_raw = (request.POST.get("value") or "").strip()
    if value_raw:
        normalized = value_raw.replace(".", "").replace(",", ".")
        try:
            job.value = Decimal(normalized)
        except InvalidOperation:
            messages.error(request, "Valor inválido.")
            return redirect("jobs")

    job.save()
    messages.success(request, "Job atualizado com sucesso!")
    return redirect("jobs")


@login_required
def cobrancas(request):
    """Lista e cadastra cobranças"""
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

    if request.method == "POST":
        form = CobrancaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cobrança cadastrada com sucesso.")
            return redirect("cobrancas")
    else:
        form = CobrancaForm()

    clients = Client.objects.order_by("name")
    jobs = Job.objects.select_related("client").order_by("title")

    context = get_base_context(request)
    context.update({
        "page_title": "Cobranças",
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
        "jobs": jobs,
    })
    
    return render(request, "cobrancas/cobrancas.html", context)


@login_required
@require_POST
def cobranca_atualizar(request):
    """Atualiza cobrança existente"""
    from datetime import datetime
    
    cobranca_id = request.POST.get("cobranca_id")
    cobranca = get_object_or_404(Cobranca, pk=cobranca_id)

    try:
        client_id = request.POST.get("client_id")
        if client_id:
            cobranca.client_id = client_id

        job_id = request.POST.get("job_id")
        cobranca.job_id = job_id if job_id else None

        number = request.POST.get("number")
        if number:
            cobranca.number = number

        raw_value = request.POST.get("value")
        if raw_value:
            cleaned = raw_value.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
            try:
                cobranca.value = Decimal(cleaned)
            except (InvalidOperation, ValueError):
                messages.error(request, "Valor inválido.")
                return redirect("cobrancas")

        # Conversão correta de datas
        issue_date = request.POST.get("issue_date")
        if issue_date:
            if isinstance(issue_date, str):
                cobranca.issue_date = datetime.strptime(issue_date, '%Y-%m-%d').date()
            else:
                cobranca.issue_date = issue_date

        due_date = request.POST.get("due_date")
        if due_date:
            if isinstance(due_date, str):
                cobranca.due_date = datetime.strptime(due_date, '%Y-%m-%d').date()
            else:
                cobranca.due_date = due_date

        payment_date = request.POST.get("payment_date")
        if payment_date and payment_date.strip():
            if isinstance(payment_date, str):
                cobranca.payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            else:
                cobranca.payment_date = payment_date
        else:
            cobranca.payment_date = None

        status = request.POST.get("status")
        if status in ("pendente", "vencida", "paga"):
            cobranca.status = status

        cobranca.notes = request.POST.get("notes", "")

        cobranca.save()
        messages.success(request, "Cobrança atualizada com sucesso.")
    except Exception as e:
        messages.error(request, f"Erro ao atualizar cobrança: {str(e)}")
    
    return redirect("cobrancas")


@login_required
def configuracoes(request):
    """Página de configurações do sistema"""
    config = SystemConfig.get_config()
    
    if request.method == 'POST':
        form = SystemConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configurações salvas com sucesso!')
            return redirect('configuracoes')
    else:
        form = SystemConfigForm(instance=config)
    
    context = get_base_context(request)
    context.update({
        'page_title': 'Configurações',
        'form': form,
        'config': config,
    })
    
    return render(request, 'configuracoes/configuracoes.html', context)


@login_required
def notificacoes_list(request):
    """Lista todas as notificações do usuário"""
    notifications = Notification.objects.filter(user=request.user)
    
    context = get_base_context(request)
    context.update({
        'page_title': 'Notificações',
        'notifications': notifications,
    })
    
    return render(request, 'notificacoes/list.html', context)


@login_required
@require_POST
def notificacao_mark_all_read(request):
    """Marca todas as notificações como lidas"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'Todas as notificações foram marcadas como lidas.')
    
    next_url = request.POST.get('next', 'dashboard')
    return redirect(next_url)


@staff_member_required
def usuarios(request):
    """Gerenciamento de usuários (apenas para staff)"""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('usuarios')
    else:
        form = UserCreateForm()
    
    users = User.objects.all().order_by('-date_joined')
    
    context = get_base_context(request)
    context.update({
        'page_title': 'Usuários',
        'users': users,
        'form': form,
    })
    
    return render(request, 'usuarios/usuarios.html', context)


@staff_member_required
@require_POST
def usuario_toggle_active(request, user_id):
    """Ativa/desativa um usuário"""
    user = get_object_or_404(User, pk=user_id)
    
    if user == request.user:
        messages.error(request, 'Você não pode desativar sua própria conta.')
        return redirect('usuarios')
    
    user.is_active = not user.is_active
    user.save()
    
    status = 'ativado' if user.is_active else 'desativado'
    messages.success(request, f'Usuário {user.username} foi {status} com sucesso.')
    
    return redirect('usuarios')