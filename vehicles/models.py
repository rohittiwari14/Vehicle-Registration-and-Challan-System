from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


reg_number_validator = RegexValidator(
    regex=r'^[A-Z]{2}[\s-]?[0-9]{2}[\s-]?[A-Z]{1,2}[\s-]?[0-9]{1,4}$',
    message='Enter a valid registration number (e.g. MH12AB1234)'
)


class Vehicle(models.Model):

    VEHICLE_TYPE_CHOICES = [
        ('motorcycle', 'Motorcycle'),
        ('scooter', 'Scooter'),
        ('moped', 'Moped'),
    ]

    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('electric', 'Electric'),
        ('cng', 'CNG'),
    ]

    registration_number = models.CharField(
        max_length=20,
        unique=True,
        validators=[reg_number_validator],
        help_text='e.g. MH12AB1234'
    )
    owner_name = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    brand = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    year_of_manufacture = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    engine_number = models.CharField(max_length=50, unique=True)
    chassis_number = models.CharField(max_length=50, unique=True)
    registered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vehicles'
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicle_registration'
        ordering = ['-registered_at']

    def __str__(self):
        return f'{self.registration_number} — {self.owner_name}'

    @property
    def total_challan_amount(self):
        return self.challans.filter(is_paid=False).aggregate(
            total=models.Sum('fine_amount')
        )['total'] or 0

    @property
    def pending_challans_count(self):
        return self.challans.filter(is_paid=False).count()


class Challan(models.Model):
    VIOLATION_CHOICES = [
        ('overspeeding', 'Over Speeding'),
        ('signal_jump', 'Signal Jump'),
        ('no_helmet', 'Riding Without Helmet'),
        ('wrong_side', 'Driving on Wrong Side'),
        ('drunk_driving', 'Drunk Driving'),
        ('no_insurance', 'No Insurance'),
        ('no_rc', 'No Registration Certificate'),
        ('no_license', 'Driving Without License'),
        ('mobile_use', 'Using Mobile While Driving'),
        ('triple_riding', 'Triple Riding'),
        ('other', 'Other'),
    ]

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='challans'
    )
    challan_number = models.CharField(max_length=20, unique=True, editable=False)
    violation_type = models.CharField(max_length=50, choices=VIOLATION_CHOICES)
    violation_date = models.DateField()
    violation_location = models.CharField(max_length=200)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='issued_challans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehicle_challan'
        ordering = ['-created_at']

    def __str__(self):
        return f'Challan {self.challan_number} — {self.vehicle.registration_number}'

    def save(self, *args, **kwargs):
        if not self.challan_number:
            self.challan_number = self._generate_challan_number()
        super().save(*args, **kwargs)

    def _generate_challan_number(self):
        import random
        import string
        from django.utils import timezone
        year = timezone.now().year
        rand_part = ''.join(random.choices(string.digits, k=6))
        return f'CHL{year}{rand_part}'
