from django.db import models
from apps.common.models import BaseModel
from django.contrib.auth import get_user_model
from apps.cases.models import FIR

User = get_user_model()

class InvestigationLog(BaseModel):
    fir = models.ForeignKey(FIR, on_delete=models.CASCADE, related_name='logs')
    entry_date_time = models.DateTimeField(auto_now_add=True)
    notes = models.TextField()
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recorded_logs'
    )

    def __str__(self):
        repr_val = self.notes[:20] + '...' if len(self.notes) > 20 else self.notes
        return f"Log for {self.fir.fir_number} by {self.recorded_by.username if self.recorded_by else 'Unknown'}: {repr_val}"
