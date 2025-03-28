from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParentViewSet, LoginView, ChildViewSet
from drf_yasg.views import get_schema_view as yasg_schema_view
from drf_yasg import openapi
from django.contrib import admin
from.import views
from django.urls import path, re_path,include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import *
from .views import get_available_slots
from rest_framework.routers import DefaultRouter
from rest_framework.routers import DefaultRouter
# Router setup
# router = DefaultRouter()
# router.register(r'register', ParentViewSet, basename='register')
# router.register(r'children', ChildViewSet, basename='child')  

# # Swagger schema view
# schema_view = yasg_schema_view(
#     openapi.Info(
#         title="Parent API",
#         default_version='v1',
#         description="API for Parent Registration & Login",
#     ),
#     public=True,
# )

# urlpatterns = [
#     path('', include(router.urls)),  # Includes all Parent endpoints
#     path('login/', LoginView.as_view(), name='login'),
    
#     # Swagger documentation
#     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
#     path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc-ui'),
#     # path('request-stock/', request_stock, name='request_stock'),
# ]
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



router = DefaultRouter()
# router.register(r"service_registration",ServiceProviderRegisterView)
router.register(r"parent_registration",ParentViewSet,basename='user_registration')
router.register(r"child_registration",ChildViewSet,basename='child_registration')
router.register(r'bookings', BookingViewSet, basename='booking')



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
    path('login/', LoginView.as_view(),name='login'),
    path('slots/', get_available_slots, name='get_available_slots'),
    path('child_list/',ViewChildListView.as_view({'get':'list'}),name='child_list'),
    path('view_profile/',ViewProfielView.as_view({'get':'list'}),name='view_profile'),
    path('view_single_child/',ViewSingleChildView.as_view({'get':'list'}),name='view_single_child'),
    path('timeslot/',ViewTimeSlotView.as_view({'get':'list'}),name='timeslot'),
    path('health_provider_list/',ListHealthProviderView.as_view({'get':'list'}),name='health_provider_list'),
    path('health_provider_details/',ViewHealthProviderDetailsView.as_view({'get':'list'}),name='health_provider_details'),
    path('vaccination_history/',VaccinationHistoryView.as_view({'get':'list'}),name='vaccination_history'),
]   


