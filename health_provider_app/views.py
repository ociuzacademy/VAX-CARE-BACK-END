from rest_framework.response import Response
from rest_framework import status, generics, viewsets,permissions
from django.shortcuts import get_object_or_404
from health_provider_app.models import StockRequest
from admin_app.models import *
from health_provider_app.serializers import *
from rest_framework.views import APIView
from django.db.models import Count
from datetime import datetime, timedelta
from user_app.models import *
# List all available vaccines
class VaccineListView(generics.ListAPIView):
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer
 

# Health providers request vaccine stock
class StockRequestViewSet(viewsets.ModelViewSet):
    queryset = StockRequest.objects.all()
    serializer_class = StockRequestSerializer
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        health_provider_id = request.data.get('health_provider')
        age_group = request.data.get('age_group')
        quantity = request.data.get('quantity')

        if not all([health_provider_id, age_group, quantity]):
            return Response({"error": "Health provider, age group, and quantity are required."}, status=400)

        # Validate health provider
        try:
            health_provider = HealthProvider.objects.get(id=health_provider_id)
        except HealthProvider.DoesNotExist:
            return Response({"error": "Invalid health provider ID."}, status=400)

        # Fetch vaccines matching the age group
        vaccines = Vaccine.objects.filter(age_group=age_group)
        if not vaccines.exists():
            return Response({"error": f"No vaccines found for the age group: {age_group}."}, status=400)

        # Create a stock request
        stock_request = StockRequest.objects.create(
            health_provider=health_provider,
            age_group=age_group,
            quantity=quantity
        )
        
        # Associate vaccines and save
        stock_request.vaccines.set(vaccines)
        stock_request.save()

        # Serialize and return the response
        serializer = self.get_serializer(stock_request)
        return Response({"message": "Stock request submitted successfully", "data": serializer.data}, status=201)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                parent = HealthProvider.objects.get(email=email)
                if parent.password == password:  #  Plaintext password check (Not secure)
                    return Response({"status":"success","message": "Login successful","user":parent.id,"name":parent.name}, status=status.HTTP_200_OK)
                return Response({"status":"failed","error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
            except HealthProvider.DoesNotExist:
                return Response({"status":"failed","error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ViewHealthProviderProfileView(viewsets.ReadOnlyModelViewSet):
    serializer_class = HealthProviderProfileSerializer
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

        # Calculate next day's date
        next_day = datetime.today().date() + timedelta(days=1)
        booking_count = Booking.objects.filter(health_provider=hp, date=next_day).count()

        serializer = HealthProviderProfileSerializer(hp)
        response_data = serializer.data  # ✅ Corrected here
        response_data["next_day_booking_count"] = booking_count

        return Response(response_data, status=status.HTTP_200_OK)
    

class ViewTodaysBookingsView(viewsets.ReadOnlyModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = TodaysBookingSerializer

    def list(self, request, *args, **kwargs):
        hp_id = request.query_params.get('id')
        print("Query parameters received:", request.query_params)
        today = datetime.today().date()
        if hp_id:
            # Filter products by the provided service_centre_id
            bookings = self.queryset.filter(health_provider_id=hp_id,date=today,status="Pending")
        else:
            # If no service_centre_id is provided, return all products
            response_data = {
                "status": "failed",
                "message": "Health provider ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered queryset
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class ViewBookingDetailsView(viewsets.ReadOnlyModelViewSet):
    serializer_class = TodaysBookingSerializer
    queryset = Booking.objects.all()

    def list(self, request, *args, **kwargs):
        booking_id = request.query_params.get('id')
        print("Query parameters received:", request.query_params)

        if not booking_id:
            response_data = {
                "status": "failed",
                "message": "Booking ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
            # print("Health Provider found:", booking)
        except HealthProvider.DoesNotExist:
            print("Booking with ID", booking_id, "does not exist in the database.")
            response_data = {
                "status": "failed",
                "message": "Booking does not exist."
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        serializer = TodaysBookingSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class UpdateVaccinationStatus(generics.UpdateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingStatusSerializer
    http_method_names = ['patch']
    def patch(self, request, *args, **kwargs):
        booking_id = request.data.get('id')
        height = request.data.get('height')
        weight = request.data.get('weight')

        if not booking_id:
            return Response({"status": "failed", "message": "Booking ID is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        booking = get_object_or_404(Booking, id=booking_id)
        child = booking.child

        if height:
            child.height = height
        if weight:
            child.weight = weight
        child.save()

        booking.status = 'success'
        booking.save()
        serializer= BookingStatusSerializer(booking)
        return Response({"status": "success", "message": "Updated successfully","data":serializer.data},
                        status=status.HTTP_200_OK)
    


class ViewVaccineStock(viewsets.ReadOnlyModelViewSet):
    queryset = HealthProviderStock.objects.all()
    serializer_class = StockSerializer

    def list(self, request, *args, **kwargs):
        hp_id = request.query_params.get('id')
        if not hp_id:
            return Response({"status": "failed", "message": "Health provider ID is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        if hp_id:
            stock = HealthProviderStock.objects.filter(health_provider_id=hp_id)
        else:
            response_data = {
                "status": "failed",
                "message": "Health provider ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered queryset
        serializer = StockSerializer(stock, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        

class ViewVaccinationListView(viewsets.ReadOnlyModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = ViewVaccinationSerializer

    def list(self, request, *args, **kwargs):
        hp_id = request.query_params.get('id')
        date = request.query_params.get('date')

        if hp_id and date:
            bookings = Booking.objects.filter(health_provider_id=hp_id,date=date,status='success')
        else:
            response_data = {
                "status": "failed",
                "message": "Health provider ID is required."
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        # Serialize the filtered queryset
        serializer = ViewVaccinationSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
