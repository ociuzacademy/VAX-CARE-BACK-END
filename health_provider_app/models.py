from django.db import models
from admin_app.models import HealthProvider, Vaccine  


class StockRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    health_provider = models.ForeignKey(HealthProvider, on_delete=models.CASCADE)
    vaccines = models.ManyToManyField(Vaccine) 
    age_group = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    created_at = models.DateTimeField(auto_now_add=True)

    
class StockInventory(models.Model):
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    age_group = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.vaccine.name} ({self.age_group}) - {self.quantity} available"

