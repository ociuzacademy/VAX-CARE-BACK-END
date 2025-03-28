from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from health_provider_app.views import *
from django.contrib import admin
from.import views
from django.urls import path, re_path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import *
from rest_framework.routers import DefaultRouter
# Swagger Schema Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Vaxcare Jr API",
        default_version='v1',
        description="API documentation for Vaxcare Jr",
        terms_of_service="https://yourwebsite.com/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="Your License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"stock-requests",StockRequestViewSet)



urlpatterns = [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "redoc/",
        schema_view.with_ui("redoc", cache_timeout=0),
        name="schema-redoc",
    ),

    path("",include(router.urls)),  # Include the router URLs
    # path('stock-requests/', StockRequestViewSet.as_view({'get':'list'}), name='stock_requests'),
    path('vaccines/', VaccineListView.as_view(), name='vaccine_list'),
    path('login/', LoginView.as_view(), name='login'),
    path('health_provider_profile/',ViewHealthProviderProfileView.as_view({'get':'list'}),name='health_provider_profile'),
    path('bookings_for_today/',ViewTodaysBookingsView.as_view({'get':'list'}),name='bookings_for_today'),
    path('view_booking_details/',ViewBookingDetailsView.as_view({'get':'list'}),name='view_booking_details'),
    path('update_vaccination_status/',UpdateVaccinationStatus.as_view(),name='update_vaccination_status'),
    path('stock_list/',ViewVaccineStock.as_view({"get":'list'}),name='stock_list'),
    path('list_vaccination_history/',ViewVaccinationListView.as_view({'get':'list'}),name='list_vaccinations'),
]
