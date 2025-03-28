from django.db import models
from django.contrib.auth.models import User

from admin_app.models import HealthProvider, TimeSlot,Vaccine


class tbl_parent(models.Model):
    MOTHER = 'Mother'
    FATHER = 'Father'
    OTHER = 'Other'
    
    RELATIONSHIP_CHOICES = [
        (MOTHER, 'Mother'),
        (FATHER, 'Father'),
        (OTHER, 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=191)
    phone = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=255)
    address = models.CharField(max_length=500, null=True, blank=True)  # Address field
    relationship = models.CharField(max_length=6, choices=RELATIONSHIP_CHOICES)  # Relationship field with choices
    no_of_children = models.IntegerField(default=0)
    image = models.ImageField(upload_to='parent_photos/', blank=True, null=True)  

    def __str__(self):
        return self.name 

from datetime import date

class Child(models.Model):
    parent = models.ForeignKey(tbl_parent, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[('Male', 'male'), ('Female', 'female')])
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    birthdate = models.DateField()
    photo = models.ImageField(upload_to='child_photos/', blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)  
    blood_group = models.CharField(
        max_length=5,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('O+', 'O+'), ('O-', 'O-'),
            ('AB+', 'AB+'), ('AB-', 'AB-')
        ]
    )

    def calculate_age(self):
        """Calculate age based on birthdate."""
        today = date.today()
        return today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))

    def __str__(self):
        return f"{self.name} (Child of {self.parent.name})"


# ✅ Model for Booking
class Booking(models.Model):
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

    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    parent = models.ForeignKey(tbl_parent, on_delete=models.CASCADE)
    health_provider = models.ForeignKey(HealthProvider, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    age_group = models.CharField(max_length=50, choices=AGE_GROUP_CHOICES)  # Select Age Group
    vaccines = models.ManyToManyField(Vaccine, blank=True)  # Store vaccines based on age group
    max_children = models.IntegerField(default=10)
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.child.name} - {self.health_provider.name} ({self.time_slot.start_time} on {self.date})"



# class VaccinationHistory(models.Model):
#     vaccine = models.ForeignKey(Vaccine,on_delete=models.CASCADE,null=True,blank=True)
#     child = models.ForeignKey(Child,on_delete=models.CASCADE,null=True,blank=True)
#     booking = models.ForeignKey(Booking,on_delete=models.CASCADE,null=True,blank=True)