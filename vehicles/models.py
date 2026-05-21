from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


reg_number_validator = RegexValidator(
    regex=r'^[A-Z]{2}[\s-]?[0-9]{2}[\s-]?[A-Z]{1,2}[\s-]?[0-9]{1,4}$',
    message='Enter a valid registration number (e.g. MH12AB1234)'
)


engine_number_validator = RegexValidator(
    regex=r'^(?=.*[A-Z])(?=.*[0-9])[A-Z0-9]{6,17}$',
    message='Engine number must be 6–17 alphanumeric characters and contain both letters and digits.'
)

chassis_number_validator = RegexValidator(
    regex=r'^(?=.*[A-HJ-NPR-Z])(?=.*[0-9])[A-HJ-NPR-Z0-9]{17}$',
    message=(
        'Chassis number must be exactly 17 alphanumeric characters, '
        'contain both letters and digits, and cannot contain I, O, or Q.'
    )
)


class VehicleType(models.Model):

    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vehicle_type'
        ordering = ['name']

    def __str__(self):
        return self.name


class ViolationType(models.Model):

    name = models.CharField(max_length=100, unique=True)
    default_fine = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text='Optional default fine amount for this violation.'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'violation_type'
        ordering = ['name']

    def __str__(self):
        return self.name


class Vehicle(models.Model):

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

    vehicle_type = models.ForeignKey(
        VehicleType,
        on_delete=models.PROTECT,
        null=True,
        related_name='vehicles',
        help_text='Type of two-wheeler'
    )

    brand = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    year_of_manufacture = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)

    engine_number = models.CharField(
        max_length=17,
        unique=True,
        validators=[engine_number_validator],
        help_text='6–17 uppercase alphanumeric characters'
    )
    chassis_number = models.CharField(
        max_length=17,
        unique=True,
        validators=[chassis_number_validator],
        help_text='17-character VIN (no I, O, Q)'
    )

    registered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='vehicles'
    )

    linked_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='owned_vehicles',
        help_text='User account this vehicle belongs to (for self-service challan view).'
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

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='challans'
    )
    challan_number = models.CharField(max_length=20, unique=True, editable=False)

    violation_type = models.ForeignKey(
        ViolationType,
        on_delete=models.PROTECT,
        null=True,
        related_name='challans',
        help_text='Type of traffic violation'
    )

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
