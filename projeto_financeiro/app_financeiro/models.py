from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone


class Client(models.Model):
    TYPE_CHOICES = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
    ]

    name = models.CharField(max_length=255)
    document = models.CharField(max_length=32, blank=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default='CPF')
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """Validações de unicidade em nível de modelo"""
        qs = Client.objects.exclude(pk=self.pk)

        # CPF único (se for CPF e preenchido)
        if self.type == 'CPF' and self.document:
            doc_clean = ''.join(filter(str.isdigit, self.document))
            if doc_clean and qs.filter(
                document__regex=doc_clean.replace('.', '').replace('-', ''),
                type='CPF'
            ).exists():
                raise ValidationError({'document': 'Já existe um cliente com este CPF.'})

        # CNPJ único (se for CNPJ e preenchido)
        if self.type == 'CNPJ' and self.document:
            doc_clean = ''.join(filter(str.isdigit, self.document))
            if doc_clean and qs.filter(
                document__regex=doc_clean,
                type='CNPJ'
            ).exists():
                raise ValidationError({'document': 'Já existe um cliente com este CNPJ.'})

        # Telefone único (somente se preenchido)
        if self.phone:
            phone_clean = ''.join(filter(str.isdigit, self.phone))
            if phone_clean and len(phone_clean) >= 10:
                if qs.filter(phone__regex=phone_clean).exists():
                    raise ValidationError({'phone': 'Já existe um cliente com este telefone.'})

        # Email único (somente se preenchido)
        if self.email:
            if qs.filter(email__iexact=self.email).exists():
                raise ValidationError({'email': 'Já existe um cliente com este email.'})

    def save(self, *args, **kwargs):
        # Converte strings vazias em None
        if self.email == '':
            self.email = None
        if self.phone == '':
            self.phone = None
        
        # Executa validação antes de salvar
        try:
            self.full_clean()
        except ValidationError:
            pass  # Ignora erros de validação no save automático
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Job(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("em_andamento", "Em andamento"),
        ("concluido", "Concluído"),
    ]

    title = models.CharField("Título", max_length=255)
    client = models.ForeignKey(
        Client,
        verbose_name="Cliente",
        on_delete=models.PROTECT,
        related_name="jobs",
    )
    value = models.DecimalField("Valor", max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField("Data de início")
    delivery_date = models.DateField("Data de entrega")
    status = models.CharField(
        "Status",
        max_length=20,
        choices=STATUS_CHOICES,
        default="pendente",
    )
    progress = models.PositiveIntegerField("Progresso (%)", default=0)
    description = models.TextField("Descrição", blank=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        ordering = ["-start_date", "title"]

    def __str__(self):
        return self.title


class Cobranca(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("vencida", "Vencida"),
        ("paga", "Paga"),
    ]

    number = models.CharField("Número", max_length=30, unique=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="cobrancas",
        verbose_name="Cliente",
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cobrancas",
        verbose_name="Job (opcional)",
    )
    value = models.DecimalField("Valor", max_digits=10, decimal_places=2)
    issue_date = models.DateField("Data de emissão")
    due_date = models.DateField("Data de vencimento")
    payment_date = models.DateField("Data de pagamento", null=True, blank=True)
    status = models.CharField(
        "Status",
        max_length=10,
        choices=STATUS_CHOICES,
        default="pendente",
    )
    last_reminder = models.DateField(
        "Último lembrete",
        null=True,
        blank=True,
    )
    notes = models.TextField("Observações", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date", "-id"]
        verbose_name = "Cobrança"
        verbose_name_plural = "Cobranças"

    def __str__(self):
        return f"{self.number} - {self.client.name}"

    def save(self, *args, **kwargs):
        # Atualiza status automaticamente baseado na data
        if self.status != 'paga' and self.due_date:
            today = timezone.localdate()
            # Converte due_date para date se for string
            if isinstance(self.due_date, str):
                from datetime import datetime
                self.due_date = datetime.strptime(self.due_date, '%Y-%m-%d').date()
            
            if self.due_date < today:
                self.status = 'vencida'
            else:
                self.status = 'pendente'
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == "paga" or not self.due_date:
            return False
        today = timezone.localdate()
        return today > self.due_date

    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        today = timezone.localdate()
        return (today - self.due_date).days

    @property
    def days_to_due(self):
        if self.status == "paga" or not self.due_date or self.is_overdue:
            return 0
        today = timezone.localdate()
        return (self.due_date - today).days


class SystemConfig(models.Model):
    """Configurações do sistema"""
    # Dados da empresa
    company_name = models.CharField("Razão Social", max_length=255, default="Amazônia Engenharia")
    company_cnpj = models.CharField("CNPJ", max_length=20, default="12.345.678/0001-90")
    company_email = models.EmailField("Email", default="admin@amazoniaengenharia.com")
    company_phone = models.CharField("Telefone", max_length=20, default="(92) 99999-9999")
    company_address = models.TextField("Endereço", default="Rua das Palmeiras, 123 - Manaus, AM")
    
    # WhatsApp/Evolution API
    whatsapp_enabled = models.BooleanField("WhatsApp ativo", default=False)
    evolution_api_url = models.CharField("URL Evolution API", max_length=255, blank=True)
    evolution_api_key = models.CharField("API Key", max_length=255, blank=True)
    evolution_instance_name = models.CharField("Nome da Instância", max_length=100, blank=True)
    evolution_sandbox = models.BooleanField("Modo Sandbox", default=True)
    
    # Lembretes automáticos
    reminder_days_before = models.PositiveIntegerField("Dias antes do vencimento", default=3)
    reminder_days_after = models.PositiveIntegerField("Dias após vencimento", default=5)
    reminder_on_due_date = models.BooleanField("Enviar no vencimento", default=True)
    reminder_include_weekends = models.BooleanField("Incluir finais de semana", default=False)
    reminder_business_hours_only = models.BooleanField("Apenas horário comercial", default=True)
    
    # Templates de mensagem
    template_before = models.TextField(
        "Template antes do vencimento",
        default="Olá {nome}! 🌿\nLembrete amigável: sua fatura no valor de {valor} vence em {dias_restantes} dia(s) ({vencimento}).\n\nPara evitar transtornos, realize o pagamento até a data de vencimento.\n\n*Amazônia Engenharia*"
    )
    template_due = models.TextField(
        "Template no vencimento",
        default="Olá {nome}! 📅\nSua fatura no valor de {valor} vence hoje ({vencimento}).\n\nPor favor, realize o pagamento para manter seus serviços em dia.\n\n*Amazônia Engenharia*"
    )
    template_after = models.TextField(
        "Template após vencimento",
        default="Olá {nome}! ⚠️\nSua fatura no valor de {valor} está vencida desde {vencimento}.\n\nEntre em contato conosco para regularizar a situação.\n\n*Amazônia Engenharia*"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração do Sistema"
        verbose_name_plural = "Configurações do Sistema"
    
    def __str__(self):
        return f"Configurações - {self.company_name}"
    
    @classmethod
    def get_config(cls):
        """Retorna a configuração atual ou cria uma padrão"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class Notification(models.Model):
    """Notificações do sistema"""
    TYPE_CHOICES = [
        ('cobranca_vencendo', 'Cobrança Vencendo'),
        ('cobranca_vencida', 'Cobrança Vencida'),
        ('job_proximo_entrega', 'Job Próximo da Entrega'),
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='info')
    title = models.CharField(max_length=255)
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"