from django.shortcuts import render
from rest_framework import parsers
from admin_app.models import TimeSlot, HealthProvider
from rest_framework.decorators import api_view
from .serializers import TimeSlotSerializer
from rest_framework import viewsets, status,generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import tbl_parent, Child
from .serializers import *
from django.db.models import F, Func, FloatField
from datetime import datetime
from admin_app.models import *
# Register API

class ParentViewSet(viewsets.ModelViewSet):
    queryset = tbl_parent.objects.all()
    serializer_class = ParentSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        print(request.FILES)  # Debugging: Check if image is being received
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            parent = serializer.save()
            return Response(
                {"status": "success", "message": "User registered successfully!", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        
        return Response(
            {"status": "failed", "message": "Validation failed", "data": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


# Login API
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                parent = tbl_parent.objects.get(email=email)
                if parent.password == password:  # Plaintext password check (Not secure)
                    parent_data = pserializer(parent).data # Serialize parent object
                    print(parent_data)
                    return Response({"status": "success", "message": "Login successful", "data": parent_data}, status=status.HTTP_200_OK)
                
                return Response({"status": "failed", "message": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            except tbl_parent.DoesNotExist:
                return Response({"status": "failed", "message": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ChildViewSet(viewsets.ModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            child = serializer.save()
            age = child.calculate_age()  # Use the method to get the child's age

            parent = child.parent
            parent.no_of_children += 1
            parent.save(update_fields=['no_of_children'])

            return Response(
                {
                    "status": "success",
                    "message": "Child added successfully!",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "status": "failed",
                "message": "Validation failed",
                "data": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
    

class UpdateParentProfile(generics.UpdateAPIView):
    queryset = tbl_parent.objects.all()
    serializer_class = ParentSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        parent_id = request.data.get('id')
        if not parent_id:
            return Response({"status": "failed", "message": "Parent ID is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        parent = get_object_or_404(tbl_parent, id=parent_id)
        serializer = ParentSerializer(parent, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "Parent profile updated successfully", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"status": "failed", "message": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class UpdateChildProfile(generics.UpdateAPIView):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer
    http_method_names = ['patch']

    def patch(self, request, *args, **kwargs):
        child_id = request.data.get('id')
        if not child_id:
            return Response({"status": "failed", "message": "Child ID is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        child = get_object_or_404(Child, id=child_id)
        serializer = ChildSerializer(child, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "Child profile updated successfully", "data": serializer.data},
                            status=status.HTTP_200_OK)
        return Response({"status": "failed", "message": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


class ViewChildListView(viewsets.ReadOnlyModelViewSet):
    queryset = Child.objects.all()
    serializer_class = ChildSerializer

    def list(self, request, *args, **kwargs):
        # Retrieve the service_centre_id from the request body
        parent_id = request.query_params.get('id')
        print("Query parameters received:", request.query_params)

        if parent_id:
            # Filter products by the provided service_centre_id
            children = self.queryset.filter(parent_id=parent_id)
        else:
            # If no service_centre_id is provided, return all products
            response_data = {
                "status": "failed",
                "message": "Parent ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered queryset
        serializer = self.get_serializer(children, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ViewSingleChildView(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChildSerializer
    queryset = Child.objects.all()

    def list(self, request, *args, **kwargs):
        child_id = request.query_params.get('id')
        print("Query parameters received:", request.query_params)

        if not child_id:
            response_data = {
                "status": "failed",
                "message": "Child ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            child = Child.objects.get(id=child_id)
            print("Child found:", child)
        except Child.DoesNotExist:
            print("Child with ID", child_id, "does not exist in the database.")
            response_data = {
                "status": "failed",
                "message": "Child does not exist."
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        serializer = ChildSerializer(child)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def get_available_slots(request):
    provider_id = request.GET.get('provider_id')  # Read from query parameter
    
    if not provider_id:
        return Response({"error": "Provider ID is required."}, status=400)

    try:
        health_provider = HealthProvider.objects.get(id=provider_id)
        slots = TimeSlot.objects.filter(health_provider=health_provider)
        
        if not slots.exists():
            return Response({"message": "No slots available."}, status=200)

        serializer = TimeSlotSerializer(slots, many=True)
        return Response(serializer.data, status=200)

    except HealthProvider.DoesNotExist:
        return Response({"error": "Health provider not found."}, status=404)
    
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Booking, TimeSlot, HealthProvider, Child,Vaccine
from .serializers import BookingSerializer
from datetime import date as datetime_date
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Booking, Child, HealthProvider, TimeSlot, Vaccine
from .serializers import BookingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    http_method_names = ['post']
    def create(self, request, *args, **kwargs):
        child_id = request.data.get('child')
        health_provider_id = request.data.get('health_provider')
        time_slot_id = request.data.get('time_slot')
        date = request.data.get('date')

        if not all([child_id, health_provider_id, time_slot_id, date]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the date is valid and not in the past
        try:
            booking_date = datetime_date.fromisoformat(date)
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if booking_date < datetime_date.today():
            return Response({"error": "Booking date cannot be in the past."}, status=status.HTTP_400_BAD_REQUEST)


        try:
            # Fetch the child and health provider safely
            child = get_object_or_404(Child, id=child_id)
            health_provider = get_object_or_404(HealthProvider, id=health_provider_id)

            # Ensure the time slot exists for the selected health provider
            time_slot = TimeSlot.objects.filter(id=time_slot_id, health_provider=health_provider).first()
            if not time_slot:
                return Response({"error": "Time slot not found for the selected health provider."}, status=status.HTTP_404_NOT_FOUND)

            # Ensure the child has a parent
            if not child.parent:
                return Response({"error": "Child must have a parent."}, status=status.HTTP_400_BAD_REQUEST)

            child_age = child.calculate_age()

        # Determine age group
            if child_age < 1:
                age_group = "6 Weeks" if child_age < 0.2 else "10 Weeks" if child_age < 0.3 else "14 Weeks"
            elif 1 <= child_age < 2:
                age_group = "9-12 Months"
            elif 2 <= child_age < 5:
                age_group = "16-24 Months"
            elif 5 <= child_age < 10:
                age_group = "5-6 Years"
            elif 10 <= child_age < 16:
                age_group = "10 Years"
            else:
                age_group = "16 Years"

            # Retrieve vaccines for this age group
            vaccines = Vaccine.objects.filter(age_group=age_group)

            # Create the booking
            booking = Booking.objects.create(
                child=child,
                parent=child.parent,
                health_provider=health_provider,
                time_slot=time_slot,
                date=date,
                age_group=age_group
            )

            # Assign vaccines
            booking.vaccines.set(vaccines)
            
            # time_slot.available_spots -= 1
            # time_slot.save()

            for vaccine in vaccines:
                    stock_entry = HealthProviderStock.objects.filter(
                        health_provider=health_provider,
                        vaccine=vaccine,
                        age_group=age_group
                    ).first()

                    if stock_entry:
                        if stock_entry.stock > 0:
                            stock_entry.stock -= 1
                            stock_entry.save()
                        else:
                            return Response(
                                {"error": f"Stock unavailable for {vaccine.vaccine_name}"},
                                status=status.HTTP_400_BAD_REQUEST
                            )

            # Serialize and return the response
            serializer = BookingSerializer(booking)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except TimeSlot.DoesNotExist:
            return Response({"error": "Time slot not found."}, status=status.HTTP_404_NOT_FOUND)

        except Child.DoesNotExist:
            return Response({"error": "Child not found."}, status=status.HTTP_404_NOT_FOUND)

        except HealthProvider.DoesNotExist:
            return Response({"error": "Health provider not found."}, status=status.HTTP_404_NOT_FOUND)


class ViewProfielView(viewsets.ReadOnlyModelViewSet):
    queryset = tbl_parent.objects.all()
    serializer_class = ParentSerializer

    def list(self, request, *args, **kwargs):
        parent_id = request.query_params.get('id')
        if not parent_id:
            response_data = {
                "status": "failed",
                "message": "Parent ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            host = tbl_parent.objects.get(id=parent_id)
            print("user found:", host)
        except parent_id.DoesNotExist:
            print("Parent with ID", parent_id, "does not exist in the database.")
            response_data = {
                "status": "failed",
                "message": "Host does not exist."
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        serializer = ParentSerializer(host)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ViewTimeSlotView(viewsets.ReadOnlyModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer

    def list(self, request, *args, **kwargs):
        hp_id = request.query_params.get('id')
        print("Query parameters received:", request.query_params)

        if hp_id:
            # Filter products by the provided service_centre_id
            timeslots = self.queryset.filter(health_provider=hp_id, available_spots__gt=0)
        else:
            # If no service_centre_id is provided, return all products
            response_data = {
                "status": "failed",
                "message": "Health provider ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered queryset
        serializer = self.get_serializer(timeslots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ListHealthProviderView(viewsets.ReadOnlyModelViewSet):
    queryset = HealthProvider.objects.all()
    serializer_class = HealthProviderSerializer

    AGE_GROUP_MAPPING = {
        (0, 6): "6 Weeks",
        (7, 10): "10 Weeks",
        (11, 14): "14 Weeks",
        (15, 52): "9-12 Months",
        (53, 104): "16-24 Months",
        (105, 312): "5-6 Years",
        (313, 520): "10 Years",
        (521, float('inf')): "16 Years",
    }

    def get_age_group(self, age_in_weeks):
        for (start, end), group in self.AGE_GROUP_MAPPING.items():
            if start <= age_in_weeks <= end:
                return group
        return None

    def list(self, request, *args, **kwargs):
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        child_id = request.query_params.get('child_id')
        
        if latitude is None or longitude is None or child_id is None:
            return Response({"error": "Latitude, longitude, and child_id are required."}, status=400)
        
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            child = Child.objects.get(id=child_id)
        except (ValueError, Child.DoesNotExist):
            return Response({"error": "Invalid latitude, longitude, or child_id."}, status=400)
        
        # Calculate child's age in weeks
        today = datetime.today().date()
        age_in_weeks = (today - child.birthdate).days // 7
        age_group = self.get_age_group(age_in_weeks)
        
        if not age_group:
            return Response({"error": "No matching age group found."}, status=400)
        
        # Filter health providers that have vaccines suitable for the given age group
        health_providers = HealthProvider.objects.filter(vaccines__age_group=age_group).distinct()
        
        # Basic distance calculation (Not actual geographical distance)
        health_providers = health_providers.annotate(
            distance=(
                Func(F('latitude') - latitude, function='ABS', output_field=FloatField()) +
                Func(F('longitude') - longitude, function='ABS', output_field=FloatField())
            )
        ).order_by('distance')
        
        serializer = self.get_serializer(health_providers, many=True)
        return Response(serializer.data)

class ViewHealthProviderDetailsView(viewsets.ReadOnlyModelViewSet):
    serializer_class = HealthProviderSerializer
    queryset = HealthProvider.objects.all()

    def list(self, request, *args, **kwargs):
        hp_id = request.query_params.get('id')
        print("Query parameters received:", request.query_params)

        if not hp_id:
            response_data = {
                "status": "failed",
                "message": "Health provider ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            hp = HealthProvider.objects.get(id=hp_id)
            print("Health Provider found:", hp)
        except HealthProvider.DoesNotExist:
            print("Health provider with ID", hp_id, "does not exist in the database.")
            response_data = {
                "status": "failed",
                "message": "Health provider does not exist."
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        serializer = HealthProviderSerializer(hp)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ViewBookingHistoryView(viewsets.ReadOnlyModelViewSet):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer

    def list(self, request, *args, **kwargs):
        hp_id = request.query_params.get('id')
        print("Query parameters received:", request.query_params)

        if hp_id:
            # Filter products by the provided service_centre_id
            timeslots = self.queryset.filter(health_provider=hp_id, available_spots__gt=0)
        else:
            # If no service_centre_id is provided, return all products
            response_data = {
                "status": "failed",
                "message": "Health provider ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered queryset
        serializer = self.get_serializer(timeslots, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# class ChildVaccineHistoryView(viewsets.ReadOnlyModelViewSet):
#     queryset = Booking.objects.all()

#     def list(self, request, *args, **kwargs):
#         child_id = request.query_params.get('id')
#         if not child_id:
#             return Response({"status": "failed", "message": "Child ID is required."},
#                             status=status.HTTP_400_BAD_REQUEST)

#         if child_id:
#             history = Booking.objects.filter(child_id=child_id)
#         else:
#             response_data = {
#                 "status": "failed",
#                 "message": "Child ID is required."
#             }
#             return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

#         # Serialize the filtered queryset
#         # serializer = StockSerializer(history, many=True)
#         # return Response(serializer.data, status=status.HTTP_200_OK)
        
from datetime import date
from django.utils.dateparse import parse_date

class VaccinationHistoryView(viewsets.ReadOnlyModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = VaccinationHistorySerializer

    def list(self, request, *args, **kwargs):
        child_id = request.query_params.get('child_id')

        if not child_id:
            return Response({"status": "failed", "message": "Child ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            child = Child.objects.get(id=child_id)
        except Child.DoesNotExist:
            return Response({"status": "failed", "message": "Child not found."}, status=status.HTTP_404_NOT_FOUND)

        # Define age groups and their corresponding age range
        AGE_GROUPS = [
            ("6 Weeks", 0.115),       # 6/52 weeks = ~0.115 years
            ("10 Weeks", 0.192),
            ("14 Weeks", 0.269),
            ("9-12 Months", 0.75),
            ("16-24 Months", 1.33),
            ("5-6 Years", 5),
            ("10 Years", 10),
            ("16 Years", 16)
        ]

        # Calculate child's age in years
        today = date.today()
        child_age_years = (today - child.birthdate).days / 365.25

        # Get completed bookings
        completed_bookings = Booking.objects.filter(child=child, status="success").values_list('age_group', flat=True)
        completed_age_groups = set(completed_bookings)

        age_groups_status = []
        upcoming_detected = False  

        for age_group, min_age in AGE_GROUPS:
            if age_group in completed_age_groups:
                age_groups_status.append({"age_group": age_group, "status": "Completed"})
            elif not upcoming_detected and child_age_years >= min_age:
                age_groups_status.append({"age_group": age_group, "status": "Missing"})
            elif child_age_years < min_age:
                age_groups_status.append({"age_group": age_group, "status": "Upcoming"})
                upcoming_detected = True
                break

        response_data = {
            "child_name": child.name,
            "age_groups": age_groups_status
        }

        serializer = VaccinationHistorySerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)