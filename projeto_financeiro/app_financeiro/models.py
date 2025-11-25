from django.db import models


class Client(models.Model):
    TYPE_CHOICES = [
        ('CPF', 'CPF'),
        ('CNPJ', 'CNPJ'),
    ]

    name = models.CharField(max_length=255)
    document = models.CharField(max_length=32, blank=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES, default='CPF')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=32, blank=True)
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
