from django.urls import path
from django.views.generic.base import RedirectView
# from .views import add_health_provider
from . import views

urlpatterns = [
   
    path('', views.admin_login, name='admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('parents/', views.parent_list, name='parent_list'),
    path('parents/<int:parent_id>/', views.parent_details, name='parent_details'),
    path('children/', views.child_details, name='child_details'),
    # path('children/<int:parent_id>/', views.child_details, name='child_details'),
    path('parents/delete/<int:parent_id>/', views.delete_parent, name='delete_parent'),
    path('admin_app/children/delete/<int:child_id>/', views.delete_child, name='delete_child'),
    path('add-vaccine/', views.add_vaccine, name='add_vaccine'),
    path('vaccine-schedule/', views.vaccine_schedule, name='vaccine_schedule'),
    path('add_health_provider/', views.add_health_provider, name='add_health_provider'),
    path('health_providers/', views.health_providers_list, name='health_providers_list'),
    path('health_providers/delete/<int:provider_id>/', views.delete_health_provider, name='delete_health_provider'),
    path('vaccine_bookings/', views.admin_bookings, name='admin_bookings'),
    path('get-vaccines-for-age-groups/', views.get_vaccines_for_age_groups, name='get_vaccines'),
    path("manage_stock/", views.manage_stock_requests, name="manage_stock"),
    path("approve_stock_request/", views.approve_stock_request, name="approve_stock_request"),
    path("reject_stock_request/", views.reject_stock_request, name="reject_stock_request"),

]
