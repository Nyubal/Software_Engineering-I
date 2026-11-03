from django.contrib.auth.models import User

from django.db import models

# Create your models here.
class Budget(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_budget = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)

    def __str__(self):
        return f"Budget for {self.user.username}: ${self.total_budget}"
