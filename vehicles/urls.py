from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('vehicles/', views.vehicle_list, name='vehicle_list'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/', views.vehicle_detail, name='vehicle_detail'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),
    path('vehicles/<int:pk>/delete/', views.vehicle_delete, name='vehicle_delete'),

    path('challans/', views.challan_list, name='challan_list'),
    path('challans/add/', views.challan_create, name='challan_create'),
    path('challans/<int:pk>/edit/', views.challan_edit, name='challan_edit'),
    path('challans/<int:pk>/delete/', views.challan_delete, name='challan_delete'),
    path('challans/<int:pk>/mark-paid/', views.mark_challan_paid, name='mark_challan_paid'),

    path('my-challans/', views.my_challans, name='my_challans'),

    path('settings/vehicle-types/', views.vehicle_type_list, name='vehicle_type_list'),
    path('settings/vehicle-types/add/', views.vehicle_type_create, name='vehicle_type_create'),
    path('settings/vehicle-types/<int:pk>/edit/', views.vehicle_type_edit, name='vehicle_type_edit'),

    path('settings/violation-types/', views.violation_type_list, name='violation_type_list'),
    path('settings/violation-types/add/', views.violation_type_create, name='violation_type_create'),
    path('settings/violation-types/<int:pk>/edit/', views.violation_type_edit, name='violation_type_edit'),
]
