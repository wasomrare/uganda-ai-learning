"""Audit log models."""
from django.db import models


class AuditLog(models.Model):
    user = models.ForeignKey('users.User', null=True, on_delete=models.SET_NULL, related_name='audit_logs')
    action = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)
    status_code = models.PositiveIntegerField()
    timestamp = models.DateTimeField(db_index=True)
    extra_data = models.JSONField(default=dict)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['user', 'timestamp'])]
