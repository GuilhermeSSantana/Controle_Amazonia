from django.contrib import admin
from .models import Client, Job, Cobranca, SystemConfig, Notification


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'document', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'type', 'created_at']
    search_fields = ['name', 'document', 'email', 'phone']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('name', 'type', 'document', 'is_active')
        }),
        ('Contato', {
            'fields': ('email', 'phone', 'address')
        }),
        ('Observações', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'value', 'status', 'progress', 'start_date', 'delivery_date']
    list_filter = ['status', 'start_date', 'delivery_date']
    search_fields = ['title', 'description', 'client__name']
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
    raw_id_fields = ['client']
    
    fieldsets = (
        ('Informações do Job', {
            'fields': ('title', 'client', 'description')
        }),
        ('Financeiro', {
            'fields': ('value',)
        }),
        ('Status e Progresso', {
            'fields': ('status', 'progress')
        }),
        ('Datas', {
            'fields': ('start_date', 'delivery_date')
        }),
    )


@admin.register(Cobranca)
class CobrancaAdmin(admin.ModelAdmin):
    list_display = ['number', 'client', 'job', 'value', 'status', 'due_date', 'payment_date', 'is_overdue']
    list_filter = ['status', 'issue_date', 'due_date', 'payment_date']
    search_fields = ['number', 'client__name', 'job__title', 'notes']
    date_hierarchy = 'due_date'
    ordering = ['-due_date']
    raw_id_fields = ['client', 'job']
    
    fieldsets = (
        ('Identificação', {
            'fields': ('number', 'client', 'job')
        }),
        ('Valores', {
            'fields': ('value', 'status')
        }),
        ('Datas', {
            'fields': ('issue_date', 'due_date', 'payment_date', 'last_reminder')
        }),
        ('Observações', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Vencida'


@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'company_cnpj', 'company_email', 'whatsapp_enabled', 'updated_at']
    
    fieldsets = (
        ('Dados da Empresa', {
            'fields': ('company_name', 'company_cnpj', 'company_email', 'company_phone', 'company_address')
        }),
        ('Configurações de WhatsApp', {
            'fields': (
                'whatsapp_enabled',
                'evolution_api_url',
                'evolution_api_key',
                'evolution_instance_name',
                'evolution_sandbox'
            ),
            'classes': ('collapse',)
        }),
        ('Lembretes Automáticos', {
            'fields': (
                'reminder_days_before',
                'reminder_days_after',
                'reminder_on_due_date',
                'reminder_include_weekends',
                'reminder_business_hours_only'
            ),
            'classes': ('collapse',)
        }),
        ('Templates de Mensagem', {
            'fields': ('template_before', 'template_due', 'template_after'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Permite apenas uma configuração
        return not SystemConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Não permite deletar a configuração
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Informações da Notificação', {
            'fields': ('user', 'type', 'title', 'message')
        }),
        ('Status', {
            'fields': ('is_read', 'link')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} notificação(ões) marcada(s) como lida(s).')
    mark_as_read.short_description = 'Marcar como lida'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} notificação(ões) marcada(s) como não lida(s).')
    mark_as_unread.short_description = 'Marcar como não lida'