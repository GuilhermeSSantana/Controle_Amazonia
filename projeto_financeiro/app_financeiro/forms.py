from django import forms
from .models import Client, Job, Cobranca
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
            # 🔽 select com os clientes já cadastrados
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
        # Só mostra clientes ativos e em ordem alfabética
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
    # valor como texto, pra aceitar 230,00
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

