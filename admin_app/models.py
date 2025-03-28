from django.db import models
from user_app.models import *  # Import both Parent and Child
from django.contrib import admin
from .models import *


class Vaccine(models.Model):
    AGE_GROUP_CHOICES = [
        ("6 Weeks", "6 Weeks"),
        ("10 Weeks", "10 Weeks"),
        ("14 Weeks", "14 Weeks"),
        ("9-12 Months", "9-12 Months"),
        ("16-24 Months", "16-24 Months"),
        ("5-6 Years", "5-6 Years"),
        ("10 Years", "10 Years"),
        ("16 Years", "16 Years"),
    ]

    VACCINE_CHOICES = [
        ("None", "None"),
        ("Oral Polio Vaccine (OPV) - 1", "Oral Polio Vaccine (OPV) - 1"),
        ("Pentavalent - 1", "Pentavalent - 1"),
        ("Rotavirus Vaccine (RVV) - 1", "Rotavirus Vaccine (RVV) - 1"),
        ("Pneumococcal Conjugate Vaccine (PCV) - 1", "Pneumococcal Conjugate Vaccine (PCV) - 1"),
        ("Inactivated Polio Vaccine (fIPV) - 1", "Inactivated Polio Vaccine (fIPV) - 1"),
        ("Pentavalent - 2", "Pentavalent - 2"),
        ("Measles & Rubella (MR) - 1", "Measles & Rubella (MR) - 1"),
        ("Diphtheria Pertussis & Tetanus (DPT) - Booster 1", "Diphtheria Pertussis & Tetanus (DPT) - Booster 1"),
    ]

    ADMINISTRATION_CHOICES = [
        ("Injection", "Injection"),
        ("Oral", "Oral"),
    ]

    PROTECTION_CHOICES = [
        ("None", "None"),
        ("Poliovirus", "Poliovirus"),
        ("Diphtheria, Pertussis, Tetanus, Hepatitis B, Hib", "Diphtheria, Pertussis, Tetanus, Hepatitis B, Hib"),
        ("Rotavirus (diarrhea)", "Rotavirus (diarrhea)"),
        ("Pneumonia, meningitis, septicemia", "Pneumonia, meningitis, septicemia"),
        ("Measles, Rubella", "Measles, Rubella"),
        ("Japanese Encephalitis", "Japanese Encephalitis"),
        ("Tetanus, Diphtheria", "Tetanus, Diphtheria"),
    ]

    SIDE_EFFECTS_CHOICES = [
        ("None", "None"),
        ("Swelling, redness, pain, fever", "Swelling, redness, pain, fever"),
        ("Mild diarrhea, vomiting, irritation", "Mild diarrhea, vomiting, irritation"),
        ("Soreness, fever", "Soreness, fever"),
        ("Redness, swelling, loss of appetite, fever", "Redness, swelling, loss of appetite, fever"),
        ("Pain, swelling, fever, headache, nausea", "Pain, swelling, fever, headache, nausea"),
    ]

    age_group = models.CharField(max_length=50, choices=AGE_GROUP_CHOICES, default="None")
    vaccine_name = models.CharField(max_length=100, choices=VACCINE_CHOICES, default="None")
    administration = models.CharField(max_length=50, choices=ADMINISTRATION_CHOICES, default="Injection")
    protection = models.CharField(max_length=100, choices=PROTECTION_CHOICES, default="None")
    side_effects = models.CharField(max_length=100, choices=SIDE_EFFECTS_CHOICES, default="None")

    def __str__(self):
        return f"{self.vaccine_name} ({self.age_group})"


class HealthProvider(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    password=models.CharField(max_length=50)
    provider_type = models.CharField(max_length=100, choices=[('Hospital', 'Hospital'), ('Health Center', 'Health Center')])
    address = models.TextField()
    phone = models.CharField(max_length=15, unique=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=7, blank=True, null=True)
    vaccines = models.ManyToManyField(Vaccine, related_name='health_providers')


    def __str__(self):
        return self.name

class HealthProviderStock(models.Model):
    health_provider = models.ForeignKey(HealthProvider, on_delete=models.CASCADE)
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=50)  # Default stock is 50 per vaccine
    age_group = models.CharField(max_length=50, choices=Vaccine.AGE_GROUP_CHOICES)

    def __str__(self):
        return f"{self.health_provider.name} - {self.vaccine.vaccine_name} ({self.stock} in stock)"

class TimeSlot(models.Model):
    health_provider = models.ForeignKey(HealthProvider, on_delete=models.CASCADE, related_name="slots")
    start_time = models.TimeField()
    end_time = models.TimeField()
    available_spots = models.IntegerField(default=15)

    def __str__(self):
        return f"{self.health_provider.name} - {self.start_time} to {self.end_time}"


class AdminLogin(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=100)  # Storing password as plain text (not secure)
    
    def __str__(self):
        return self.email






