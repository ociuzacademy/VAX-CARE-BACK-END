from rest_framework import serializers
from admin_app.models import * 
from health_provider_app.models import *
from user_app.models import *

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProvider
        fields = ['email','password']

class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = ['id', 'vaccine_name', 'age_group']  # Ensure stock_available exists

class StockRequestSerializer(serializers.ModelSerializer):
    vaccine_ids = serializers.PrimaryKeyRelatedField(many=True, read_only=True, source="vaccines")
  # Get vaccine IDs

    class Meta:
        model = StockRequest
        fields = ['id', 'health_provider', 'vaccine_ids', 'age_group', 'quantity', 'status', 'created_at']
        read_only_fields = ['vaccine_ids', 'status', 'created_at']

    def get_vaccine_ids(self, obj):
        return list(obj.vaccines.values_list('id', flat=True))  # Fetch only vaccine IDs

class HealthProviderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProvider
        fields = '__all__'


class VaccineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = ['id', 'vaccine_name', 'administration']  # Include required fields



class TodaysBookingSerializer(serializers.ModelSerializer):
    parent_name = serializers.SerializerMethodField()
    child_name = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    vaccines = VaccineSerializer(many=True, read_only=True) 

    class Meta:
        model = Booking
        fields = '__all__'
 
    def get_parent_name(self,obj):
        return obj.parent.name if obj.parent else None
    def get_child_name(self,obj):
        return obj.child.name if obj.child else None
    def get_start_time(self,obj):
        return obj.time_slot.start_time if obj.time_slot else None
    def get_end_time(self,obj):
        return obj.time_slot.end_time if obj.time_slot else None
    

class BookingStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Booking
        fields = '__all__'


class VaccinesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vaccine
        fields = ['vaccine_name', 'age_group', 'administration', 'protection', 'side_effects']

class StockSerializer(serializers.ModelSerializer):
    vaccine_details = VaccinesSerializer(source='vaccine', read_only=True)

    class Meta:
        model = HealthProviderStock
        fields = ['id','stock','health_provider','vaccine','vaccine_details']


class ViewVaccinationSerializer(serializers.ModelSerializer):
    child_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['id','child_name','parent_name','phone_number']

    def get_child_name(self,obj):
        return obj.child.name if obj.child else None
    def get_parent_name(self,obj):
        return obj.parent.name if obj.parent else None
    def get_phone_number(self,obj):
        return obj.parent.phone if obj.parent else None