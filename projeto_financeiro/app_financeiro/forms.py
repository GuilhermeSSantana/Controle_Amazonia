from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Client, Job, Cobranca, SystemConfig
from decimal import Decimal, InvalidOperation


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            "name",
            "document",
            "type",
            "email",
            "phone",
            "address",
            "notes",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input"}),
            "document": forms.TextInput(attrs={"class": "input"}),
            "type": forms.Select(attrs={"class": "select"}),
            "email": forms.EmailInput(attrs={"class": "input"}),
            "phone": forms.TextInput(attrs={"class": "input"}),
            "address": forms.Textarea(attrs={"class": "textarea"}),
            "notes": forms.Textarea(attrs={"class": "textarea"}),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "client",
            "value",
            "start_date",
            "delivery_date",
            "status",
            "progress",
            "description",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "input", "placeholder": "Título do job"}
            ),
            "client": forms.Select(attrs={"class": "select"}),
            "value": forms.NumberInput(
                attrs={"class": "input", "step": "0.01", "min": "0"}
            ),
            "start_date": forms.DateInput(
                attrs={"type": "date", "class": "input"}
            ),
            "delivery_date": forms.DateInput(
                attrs={"type": "date", "class": "input"}
            ),
            "status": forms.Select(attrs={"class": "select"}),
            "progress": forms.NumberInput(
                attrs={"class": "input", "min": 0, "max": 100}
            ),
            "description": forms.Textarea(
                attrs={"class": "textarea", "rows": 3}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["client"].queryset = Client.objects.filter(
            is_active=True
        ).order_by("name")

    def clean_progress(self):
        progress = self.cleaned_data.get("progress") or 0
        if progress < 0 or progress > 100:
            raise forms.ValidationError("O progresso deve estar entre 0 e 100%.")
        return progress


class CobrancaForm(forms.ModelForm):
    client = forms.ModelChoiceField(
        queryset=Client.objects.order_by("name"),
        label="Cliente",
        help_text="Selecione um cliente já cadastrado.",
    )
    job = forms.ModelChoiceField(
        queryset=Job.objects.select_related("client").order_by("title"),
        label="Job (opcional)",
        required=False,
        help_text="Vincule a um job/projeto, se quiser.",
    )
    value = forms.CharField(label="Valor")

    class Meta:
        model = Cobranca
        fields = [
            "number",
            "client",
            "job",
            "value",
            "status",
            "issue_date",
            "due_date",
            "payment_date",
            "notes",
        ]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "payment_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_value(self):
        raw = self.cleaned_data.get("value")
        if raw is None:
            raise forms.ValidationError("Informe um valor.")

        raw = str(raw)
        raw = (
            raw.replace("R$", "")
            .replace(" ", "")
            .replace(".", "")
            .replace(",", ".")
        )
        try:
            return Decimal(raw)
        except (InvalidOperation, ValueError):
            raise forms.ValidationError(
                "Informe um valor numérico válido. Ex: 2500,00"
            )


class SystemConfigForm(forms.ModelForm):
    class Meta:
        model = SystemConfig
        fields = [
            'company_name',
            'company_cnpj',
            'company_email',
            'company_phone',
            'company_address',
            'whatsapp_enabled',
            'evolution_api_url',
            'evolution_api_key',
            'evolution_instance_name',
            'evolution_sandbox',
            'reminder_days_before',
            'reminder_days_after',
            'reminder_on_due_date',
            'reminder_include_weekends',
            'reminder_business_hours_only',
            'template_before',
            'template_due',
            'template_after',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'input'}),
            'company_cnpj': forms.TextInput(attrs={'class': 'input'}),
            'company_email': forms.EmailInput(attrs={'class': 'input'}),
            'company_phone': forms.TextInput(attrs={'class': 'input'}),
            'company_address': forms.Textarea(attrs={'class': 'textarea', 'rows': 2}),
            'whatsapp_enabled': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'evolution_api_url': forms.TextInput(attrs={'class': 'input', 'placeholder': 'https://sua-instancia-evolution.com'}),
            'evolution_api_key': forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Chave secreta'}),
            'evolution_instance_name': forms.TextInput(attrs={'class': 'input', 'placeholder': 'amazonia-engenharia'}),
            'evolution_sandbox': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'reminder_days_before': forms.NumberInput(attrs={'class': 'input', 'min': 0, 'max': 30}),
            'reminder_days_after': forms.NumberInput(attrs={'class': 'input', 'min': 0, 'max': 30}),
            'reminder_on_due_date': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'reminder_include_weekends': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'reminder_business_hours_only': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'template_before': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'template_due': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
            'template_after': forms.Textarea(attrs={'class': 'textarea', 'rows': 4}),
        }


class UserCreateForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'input', 'placeholder': 'email@exemplo.com'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Nome'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Sobrenome'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input', 'placeholder': 'nomedeusuario'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'checkbox'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'input'})
        self.fields['password2'].widget.attrs.update({'class': 'input'})