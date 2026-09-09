from django.contrib import admin
from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 'user', 'action', 'model_name', 'object_repr', 'ip_address','extra_info'
    )
    list_filter = ('action', 'model_name', 'user')
    search_fields = ('object_repr', 'extra_info', 'ip_address', 'user__username')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp', 'user', 'action', 'model_name', 'object_repr','object_data', 'extra_info', 'ip_address')

    # غیرفعال کردن افزودن
    def has_add_permission(self, request):
        return False

    # غیرفعال کردن حذف
    def has_delete_permission(self, request, obj=None):
        return False
   
    # غیرفعال کردن ویرایش
    def has_change_permission(self, request, obj=None):
        return False
