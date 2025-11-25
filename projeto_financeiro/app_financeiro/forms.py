from django import forms
from .models import Client


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
