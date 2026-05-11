from django.db import models
from core.models import BaseModel


class Upload(BaseModel):
    uploaded_by = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='uploads')
    file = models.FileField(upload_to='uploads/%Y/%m/')
    original_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=50)
    file_size = models.PositiveIntegerField(default=0)
    is_approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'uploads'
        ordering = ['-created_at']
