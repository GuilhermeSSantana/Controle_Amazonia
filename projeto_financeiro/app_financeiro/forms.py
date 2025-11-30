from django import forms
from .models import Client
from .models import Job


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
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Título do job"}),
            "client": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome do cliente"}),
            "value": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "delivery_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "progress": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 100}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def clean_progress(self):
        progress = self.cleaned_data.get("progress") or 0
        if progress < 0 or progress > 100:
            raise forms.ValidationError("O progresso deve estar entre 0 e 100%.")
        return progress