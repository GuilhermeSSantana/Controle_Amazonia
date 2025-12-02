from django.db import models
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
    
    # ✅ CORREÇÃO: removido unique=True, mas mantém validação no clean()
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True, null=True)
    
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Validações de unicidade em nível de modelo,
        ignorando o próprio registro na edição.
        """
        qs = Client.objects.exclude(pk=self.pk)

        # CPF único (se for CPF)
        if self.type == 'CPF' and self.document:
            if qs.filter(document=self.document, type='CPF').exists():
                raise ValidationError("Já existe um cliente com este CPF.")

        # Telefone único (somente se preenchido)
        if self.phone:
            if qs.filter(phone=self.phone).exists():
                raise ValidationError("Já existe um cliente com este telefone.")

        # Email único (somente se preenchido)
        if self.email:
            if qs.filter(email=self.email).exists():
                raise ValidationError("Já existe um cliente com este email.")

    def save(self, *args, **kwargs):
        # Converte strings vazias em None para campos que podem ser nulos
        if self.email == '':
            self.email = None
        if self.phone == '':
            self.phone = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("em_andamento", "Em andamento"),
        ("concluido", "Concluído"),
    ]

    title = models.CharField("Título", max_length=255)

    # 🔗 RELACIONAL: cada job pertence a um Client
    client = models.ForeignKey(
        Client,
        verbose_name="Cliente",
        on_delete=models.PROTECT,
        related_name="jobs",
    )

    value = models.DecimalField("Valor", max_digits=12, decimal_places=2)
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


# ✅ CORREÇÃO: Cobranca agora está FORA da classe Job
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