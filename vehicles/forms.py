import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Vehicle, Challan, VehicleType, ViolationType


class LoginForm(AuthenticationForm):
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter your password',
        })
    )


class VehicleTypeForm(forms.ModelForm):
    
    class Meta:
        model = VehicleType
        fields = ['name', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Scooter, Moped, Bike',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip().title()


class ViolationTypeForm(forms.ModelForm):
    
    class Meta:
        model = ViolationType
        fields = ['name', 'default_fine', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Over Speeding, Signal Jump',
            }),
            'default_fine': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Default fine in ₹ (optional)',
                'min': 0,
                'step': '0.01',
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_name(self):
        return self.cleaned_data['name'].strip().title()


class VehicleForm(forms.ModelForm):
    
    class Meta:
        model = Vehicle
        fields = [
            'registration_number', 'owner_name', 'vehicle_type',
            'brand', 'model_name', 'year_of_manufacture',
            'fuel_type', 'engine_number', 'chassis_number', 'linked_user',
        ]
        widgets = {
            'registration_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. MH12AB1234',
            }),
            'owner_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Full name of vehicle owner',
            }),
            'vehicle_type': forms.Select(attrs={'class': 'form-select'}),
            'brand': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Honda, Bajaj, TVS',
            }),
            'model_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. Activa, Pulsar',
            }),
            'year_of_manufacture': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. 2021',
                'min': 1980,
                'max': timezone.now().year,
            }),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'engine_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. ABC1234567 (6–17 uppercase alphanumeric)',
            }),
            'chassis_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. MA3EWDE1S00123456 (17 characters, no I/O/Q)',
            }),
            'linked_user': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['vehicle_type'].queryset = VehicleType.objects.filter(is_active=True)
        self.fields['vehicle_type'].empty_label = '— Select vehicle type —'
        self.fields['linked_user'].required = False
        self.fields['linked_user'].empty_label = '— Link to a user account (optional) —'
        self.fields['linked_user'].help_text = (
            'Link this vehicle to a user account so they can see their challans.'
        )

    def clean_registration_number(self):
        reg = self.cleaned_data['registration_number'].upper().replace(' ', '').replace('-', '')
        return reg

    def clean_engine_number(self):
        engine = self.cleaned_data['engine_number'].upper().strip()
        engine = engine.replace(' ', '').replace('-', '').replace('/', '')

        if not re.match(r'^[A-Z0-9]{6,17}$', engine):
            raise forms.ValidationError(
                'Engine number must be 6–17 characters using only letters and digits. '
                'Remove any spaces, hyphens, or special characters.'
            )
        if not re.search(r'[A-Z]', engine):
            raise forms.ValidationError(
                'Engine number must contain at least one letter (e.g. ABC1234567).'
            )
        if not re.search(r'[0-9]', engine):
            raise forms.ValidationError(
                'Engine number must contain at least one digit (e.g. ABC1234567).'
            )
        return engine

    def clean_chassis_number(self):
        chassis = self.cleaned_data['chassis_number'].upper().strip()
        chassis = chassis.replace(' ', '').replace('-', '').replace('/', '')

        if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', chassis):
            raise forms.ValidationError(
                'Chassis number must be exactly 17 alphanumeric characters. '
                'The letters I, O, and Q are not allowed (standard VIN format).'
            )
        if not re.search(r'[A-HJ-NPR-Z]', chassis):
            raise forms.ValidationError(
                'Chassis number must contain at least one letter (e.g. MA3EWDE1S00123456).'
            )
        if not re.search(r'[0-9]', chassis):
            raise forms.ValidationError(
                'Chassis number must contain at least one digit (e.g. MA3EWDE1S00123456).'
            )
        return chassis

    def clean_year_of_manufacture(self):
        year = self.cleaned_data['year_of_manufacture']
        current_year = timezone.now().year
        if year < 1980 or year > current_year:
            raise forms.ValidationError(f'Year must be between 1980 and {current_year}.')
        return year


class ChallanForm(forms.ModelForm):

    class Meta:
        model = Challan
        fields = [
            'vehicle', 'violation_type', 'violation_date',
            'violation_location', 'fine_amount', 'is_paid', 'remarks',
        ]
        widgets = {
            'vehicle': forms.Select(attrs={'class': 'form-select'}),
            'violation_type': forms.Select(attrs={'class': 'form-select'}),
            'violation_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date',
            }),
            'violation_location': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'e.g. MG Road, Pune',
            }),
            'fine_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': 'Fine amount in ₹',
                'min': 0,
                'step': '0.01',
            }),
            'is_paid': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'remarks': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Additional notes (optional)',
                'rows': 3,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only registered vehicles
        self.fields['vehicle'].queryset = Vehicle.objects.all().order_by('registration_number')
        self.fields['vehicle'].empty_label = '— Select a registered vehicle —'
        self.fields['violation_type'].queryset = ViolationType.objects.filter(is_active=True)
        self.fields['violation_type'].empty_label = '— Select violation type —'

    def clean_violation_date(self):
        date = self.cleaned_data['violation_date']
        if date > timezone.now().date():
            raise forms.ValidationError('Violation date cannot be in the future.')
        return date

    def clean_fine_amount(self):
        amount = self.cleaned_data['fine_amount']
        if amount <= 0:
            raise forms.ValidationError('Fine amount must be greater than zero.')
        return amount
