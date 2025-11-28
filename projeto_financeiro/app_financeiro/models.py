from django.db import models
from django.core.exceptions import ValidationError
import re

class Client(models.Model):
    TYPE_CHOICES = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
    ]

    name = models.CharField(max_length=255)
    document = models.CharField(max_length=32, blank=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default='CPF')
    email = models.EmailField(blank=True, unique=True)  # Email único
    phone = models.CharField(max_length=32, blank=True, unique=True)  # Telefone único
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Validar CPF único
        if self.type == 'CPF':
            if Client.objects.filter(document=self.document, type='CPF').exists():
                raise ValidationError("Já existe um cliente com este CPF.")
        
        # Validar telefone único
        if Client.objects.filter(phone=self.phone).exists():
            raise ValidationError("Já existe um cliente com este telefone.")

        # Validar email único
        if Client.objects.filter(email=self.email).exists():
            raise ValidationError("Já existe um cliente com este email.")

    def __str__(self):
        return self.name
