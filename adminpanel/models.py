# adminpanel/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('STATUS_CHANGE', 'Status Change'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admin_audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    object_data = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    extra_info = models.TextField(blank=True) 

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user} - {self.action} {self.model_name}({self.object_id})"
