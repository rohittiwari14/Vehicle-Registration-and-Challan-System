from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count, Sum
from .models import Vehicle, Challan
from .forms import LoginForm, VehicleForm, ChallanForm



def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            # Respect the ?next= parameter if present
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'vehicles/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')



@login_required
def dashboard(request):
    total_vehicles = Vehicle.objects.count()
    total_challans = Challan.objects.count()
    pending_challans = Challan.objects.filter(is_paid=False).count()
    total_fine_collected = Challan.objects.filter(is_paid=True).aggregate(
        total=Sum('fine_amount')
    )['total'] or 0

    recent_vehicles = Vehicle.objects.select_related('registered_by').order_by('-registered_at')[:5]
    recent_challans = Challan.objects.select_related('vehicle', 'issued_by').order_by('-created_at')[:5]

    context = {
        'total_vehicles': total_vehicles,
        'total_challans': total_challans,
        'pending_challans': pending_challans,
        'total_fine_collected': total_fine_collected,
        'recent_vehicles': recent_vehicles,
        'recent_challans': recent_challans,
    }
    return render(request, 'vehicles/dashboard.html', context)


@login_required
def vehicle_list(request):
    search_query = request.GET.get('q', '').strip()
    vehicles = Vehicle.objects.select_related('registered_by').annotate(
        challan_count=Count('challans')
    )

    if search_query:
        vehicles = vehicles.filter(
            Q(registration_number__icontains=search_query) |
            Q(owner_name__icontains=search_query) |
            Q(brand__icontains=search_query) |
            Q(model_name__icontains=search_query)
        )

    context = {
        'vehicles': vehicles,
        'search_query': search_query,
    }
    return render(request, 'vehicles/vehicle_list.html', context)


@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    challans = vehicle.challans.select_related('issued_by').all()
    context = {
        'vehicle': vehicle,
        'challans': challans,
    }
    return render(request, 'vehicles/vehicle_detail.html', context)


@login_required
def vehicle_create(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.registered_by = request.user
            vehicle.save()
            messages.success(
                request,
                f'Vehicle {vehicle.registration_number} registered successfully!'
            )
            return redirect('vehicle_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VehicleForm()

    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'form_title': 'Register New Vehicle',
        'submit_label': 'Register Vehicle',
    })


@login_required
def vehicle_edit(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, f'Vehicle {vehicle.registration_number} updated successfully!')
            return redirect('vehicle_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'form_title': f'Edit Vehicle — {vehicle.registration_number}',
        'submit_label': 'Save Changes',
        'vehicle': vehicle,
    })


@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)

    if request.method == 'POST':
        reg_num = vehicle.registration_number
        vehicle.delete()
        messages.success(request, f'Vehicle {reg_num} has been deleted.')
        return redirect('vehicle_list')

    return render(request, 'vehicles/vehicle_confirm_delete.html', {'vehicle': vehicle})



@login_required
def challan_list(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    challans = Challan.objects.select_related('vehicle', 'issued_by').all()

    if search_query:
        challans = challans.filter(
            Q(challan_number__icontains=search_query) |
            Q(vehicle__registration_number__icontains=search_query) |
            Q(vehicle__owner_name__icontains=search_query) |
            Q(violation_location__icontains=search_query)
        )

    if status_filter == 'paid':
        challans = challans.filter(is_paid=True)
    elif status_filter == 'pending':
        challans = challans.filter(is_paid=False)

    context = {
        'challans': challans,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    return render(request, 'vehicles/challan_list.html', context)


@login_required
def challan_create(request):
    initial = {}
    vehicle_pk = request.GET.get('vehicle')
    if vehicle_pk:
        initial['vehicle'] = vehicle_pk

    if request.method == 'POST':
        form = ChallanForm(request.POST)
        if form.is_valid():
            challan = form.save(commit=False)
            challan.issued_by = request.user
            if challan.is_paid:
                challan.paid_at = timezone.now()
            challan.save()
            messages.success(
                request,
                f'Challan {challan.challan_number} issued successfully!'
            )
            return redirect('challan_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChallanForm(initial=initial)

    return render(request, 'vehicles/challan_form.html', {
        'form': form,
        'form_title': 'Issue New Challan',
        'submit_label': 'Issue Challan',
    })


@login_required
def challan_edit(request, pk):
    challan = get_object_or_404(Challan, pk=pk)
    was_paid_before = challan.is_paid

    if request.method == 'POST':
        form = ChallanForm(request.POST, instance=challan)
        if form.is_valid():
            updated_challan = form.save(commit=False)
            if updated_challan.is_paid and not was_paid_before:
                updated_challan.paid_at = timezone.now()
            elif not updated_challan.is_paid:
                updated_challan.paid_at = None
            updated_challan.save()
            messages.success(request, f'Challan {challan.challan_number} updated successfully!')
            return redirect('challan_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ChallanForm(instance=challan)

    return render(request, 'vehicles/challan_form.html', {
        'form': form,
        'form_title': f'Edit Challan — {challan.challan_number}',
        'submit_label': 'Save Changes',
        'challan': challan,
    })


@login_required
def challan_delete(request, pk):
    challan = get_object_or_404(Challan, pk=pk)

    if request.method == 'POST':
        challan_num = challan.challan_number
        challan.delete()
        messages.success(request, f'Challan {challan_num} has been deleted.')
        return redirect('challan_list')

    return render(request, 'vehicles/challan_confirm_delete.html', {'challan': challan})


@login_required
def mark_challan_paid(request, pk):
    challan = get_object_or_404(Challan, pk=pk)
    if not challan.is_paid:
        challan.is_paid = True
        challan.paid_at = timezone.now()
        challan.save()
        messages.success(request, f'Challan {challan.challan_number} marked as paid.')
    else:
        messages.info(request, f'Challan {challan.challan_number} is already paid.')
    return redirect(request.META.get('HTTP_REFERER', 'challan_list'))
