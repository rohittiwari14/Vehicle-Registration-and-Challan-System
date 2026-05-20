from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from .models import Vehicle, Challan


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


class VehicleForm(forms.ModelForm):

    class Meta:
        model = Vehicle
        fields = [
            'registration_number', 'owner_name', 'vehicle_type',
            'brand', 'model_name', 'year_of_manufacture',
            'fuel_type', 'engine_number', 'chassis_number',
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
                'placeholder': 'Engine number from RC book',
            }),
            'chassis_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Chassis number from RC book',
            }),
        }

    def clean_registration_number(self):
        reg = self.cleaned_data['registration_number'].upper().replace(' ', '').replace('-', '')
        return reg

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
        self.fields['vehicle'].queryset = Vehicle.objects.all().order_by('registration_number')
        self.fields['vehicle'].empty_label = '— Select a registered vehicle —'

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
