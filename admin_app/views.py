from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from user_app.models import tbl_parent
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import HealthProvider, Vaccine, HealthProviderStock
from collections import defaultdict
from django.shortcuts import render, redirect
from health_provider_app.models import StockRequest, StockInventory
from user_app.models import  *



# Admin login
def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email == "admin@gmail.com" and password == "admin":
            messages.success(request, "Login successful")
            return redirect('dashboard')  # Fixed redirect
        else:
            messages.error(request, "Invalid email or password")
            return redirect('admin_login')

    return render(request, 'register_login.html')


# Dashboard view
def dashboard(request):
    total_parents = tbl_parent.objects.count()
    total_children = Child.objects.count()
    total_health_providers = HealthProvider.objects.count()

    return render(request, 'dashboard.html', {
        'total_parents': total_parents,
        'total_children': total_children,
        'total_health_providers': total_health_providers
    })


# Parent-related views
def parent_list(request):
    parents = tbl_parent.objects.all()
    return render(request, 'parents_details.html', {'parents': parents})


def parent_details(request, parent_id):
    parent = get_object_or_404(tbl_parent, id=parent_id)
    children = Child.objects.filter(id=parent.id)
    return render(request, 'parent_details.html', {'parent': parent},{'child':children})


def delete_parent(request, parent_id):
    parent = get_object_or_404(tbl_parent, id=parent_id)
    parent.delete()  # This should also delete children if CASCADE is set
    return redirect('parent_list')


from django.shortcuts import render
from user_app.models import Child  # Import the Child model from user_app

def child_details(request):
    children = Child.objects.all()  # Fetch all children from DB
    return render(request, 'child_details.html', {'children': children})  # Pass to template


def delete_child(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    child.delete()
    return redirect('child_details')  # Redirects to child list



# Vaccine-related views

def add_vaccine(request):
    if request.method == "POST":
        age_group = request.POST.get("age_group")
        vaccine_name = request.POST.get("vaccine_name")
        administration = request.POST.get("administration")
        protection = request.POST.get("protection")
        side_effects = request.POST.get("side_effects")

        # Ensure required fields are selected
        if not age_group or not vaccine_name or not administration or not protection:
            messages.error(request, "Please fill all required fields.")
            return redirect("add_vaccine")

        # Save the vaccine to the database
        Vaccine.objects.create(
            age_group=age_group,
            vaccine_name=vaccine_name,
            administration=administration,
            protection=protection,
            side_effects=side_effects,
        )

        messages.success(request, "Vaccine added successfully!")
        return redirect("add_vaccine")  # Redirect to clear form

    return render(request, "add_vaccine.html")


def vaccine_schedule(request):
    vaccines = Vaccine.objects.all()
    return render(request, "vaccine_schedule.html", {"vaccines": vaccines})


# Health provider-related views
from django.contrib import messages
from django.shortcuts import render, redirect
from collections import defaultdict
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import HealthProvider, Vaccine, HealthProviderStock

from collections import defaultdict
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import HealthProvider, Vaccine, HealthProviderStock
from django.contrib import messages
from django.shortcuts import render, redirect
from collections import defaultdict
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import HealthProvider, Vaccine, HealthProviderStock
from datetime import datetime, timedelta
from datetime import datetime, timedelta
from .models import HealthProvider, Vaccine, HealthProviderStock, TimeSlot


from datetime import datetime, timedelta
from collections import defaultdict
from django.contrib import messages
from django.shortcuts import render, redirect

def add_health_provider(request):
    vaccines = Vaccine.objects.all()
    grouped_vaccines = defaultdict(list)

    for vaccine in vaccines:
        grouped_vaccines[vaccine.age_group].append(vaccine)

    age_groups = Vaccine.AGE_GROUP_CHOICES

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        provider_type = request.POST.get('type', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        latitude = request.POST.get('latitude') or None
        longitude = request.POST.get('longitude') or None
        selected_age_groups = request.POST.getlist('age_group')

        if not name or not provider_type or not address or not phone or not password:
            messages.error(request, "Please fill in all required fields, including password.")
            return render(request, 'add_health_provider.html', {'grouped_vaccines': grouped_vaccines, 'age_groups': age_groups})

        if email and HealthProvider.objects.filter(email=email).exists():
            messages.error(request, "A provider with this email already exists.")
            return render(request, 'add_health_provider.html', {'grouped_vaccines': grouped_vaccines, 'age_groups': age_groups})

        try:
            # Create Health Provider
            health_provider = HealthProvider.objects.create(
                name=name,
                email=email,
                password=password,  # Plain text password (Not Secure)
                provider_type=provider_type,
                address=address,
                phone=phone,
                latitude=latitude,
                longitude=longitude
            )

            # Assign vaccines based on selected age groups
            all_vaccines = []
            for age_group in selected_age_groups:
                vaccines_for_age = Vaccine.objects.filter(age_group=age_group)
                all_vaccines.extend(vaccines_for_age)
                for vaccine in vaccines_for_age:
                    HealthProviderStock.objects.create(
                        health_provider=health_provider, 
                        vaccine=vaccine, 
                        stock=50,
                        age_group=age_group
                    )

            health_provider.vaccines.set(all_vaccines)

            # Generate Time Slots (8:00 AM - 4:00 PM, 15 mins each, 10 children per slot)
            start_time = datetime.strptime("09:00 AM", "%I:%M %p")
            end_time = datetime.strptime("03:00 PM", "%I:%M %p")
            slot_duration = timedelta(minutes=30)
            current_time = start_time

            while current_time < end_time:
                TimeSlot.objects.create(
                    health_provider=health_provider,
                    start_time=current_time.time(),
                    end_time=(current_time + slot_duration).time(),
                )
                current_time += slot_duration

            slot_count = TimeSlot.objects.filter(health_provider=health_provider).count()
            messages.success(request, f"Health provider '{name}' added successfully with {len(all_vaccines)} vaccines and {slot_count} time slots.")
            return redirect('health_providers_list')

        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return render(request, 'add_health_provider.html', {'grouped_vaccines': grouped_vaccines, 'age_groups': age_groups})

    return render(request, 'add_health_provider.html', {'grouped_vaccines': grouped_vaccines, 'age_groups': age_groups})
        

@csrf_exempt
def get_vaccines_for_age_groups(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            age_groups = data.get("age_groups", [])

            if not age_groups:
                return JsonResponse({"error": "No age groups provided"}, status=400)

            vaccines = Vaccine.objects.filter(age_group__in=age_groups).values(
                "vaccine_name", "administration", "protection", "side_effects"
            )

            return JsonResponse({"vaccines": list(vaccines)}, safe=False)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def health_providers_list(request):
    health_providers = HealthProvider.objects.all()
    return render(request, 'health_providers_list.html', {'health_providers': health_providers})


def delete_health_provider(request, provider_id):
    if request.method == "POST":  # Ensure only POST requests are allowed
        provider = get_object_or_404(HealthProvider, id=provider_id)
        provider.delete()
        messages.success(request, "Health provider deleted successfully!")
        return redirect('health_providers_list')  # Update with the correct redirect URL
    else:
        messages.error(request, "Invalid request method.")
        return redirect('health_providers_list')


def manage_stock_requests(request):
    stock_requests = StockRequest.objects.all()
    return render(request, "manage_stock.html", {"stock_requests": stock_requests})

def approve_stock_request(request):
    request_id = request.GET.get('id')
    stock_request = get_object_or_404(StockRequest, id=request_id)

    # Update stock request status
    stock_request.status = "Approved"
    stock_request.save()

    # Update stock for each vaccine associated with the request
    for vaccine in stock_request.vaccines.all():
        health_provider_stock, created = HealthProviderStock.objects.get_or_create(
            health_provider=stock_request.health_provider,
            vaccine=vaccine,
            defaults={'stock': 50}  # Set default stock if new entry
        )

        # Increase the stock quantity
        health_provider_stock.stock += stock_request.quantity
        health_provider_stock.save()

    messages.success(
        request,
        f"Stock request from {stock_request.health_provider.name} has been approved and stock updated."
    )

    return redirect("manage_stock")
  # Redirect back to the list

def reject_stock_request(request):
    request_id=request.GET.get('id')
    stock_request = get_object_or_404(StockRequest, id=request_id)
    stock_request.status = "Rejected"
    stock_request.save()
    messages.error(request, f"Stock request from {stock_request.health_provider.name} has been rejected.")
    return redirect("manage_stock")  # Redirect back to the list

def admin_bookings(request):
    bookings = Booking.objects.all()
    
    for booking in bookings:
        # Get all vaccines related to the selected age group
        booking.vaccines = Vaccine.objects.filter(age_group=booking.child.age_group)

    return render(request, 'vaccine_bookings.html', {'bookings': bookings})