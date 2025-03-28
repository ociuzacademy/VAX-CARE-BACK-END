from rest_framework import serializers
from .models import tbl_parent,Child
from admin_app.models import TimeSlot, Vaccine
from .models import Booking, Child

class ParentSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  

    class Meta:
        model = tbl_parent
        fields = '__all__'

    def validate_email(self, value):
        """Check if the email already exists."""
        if tbl_parent.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def to_representation(self, instance):
        """Override representation to modify image path."""
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = f"media/{instance.image.name}"  # Relative path
        return representation


    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class pserializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_parent
        fields = '__all__'

class ChildSerializer(serializers.ModelSerializer):\

    class Meta:
        model = Child
        fields = '__all__'

    # def get_age(self, obj):
    #     """Get the child's age dynamically."""
    #     return obj.calculate_age()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if hasattr(instance, "photo") and instance.photo:
            representation["photo"] = f"media/{instance.photo.name}"  # Relative path
        return representation


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ['id', 'start_time', 'end_time' ]


from .models import Child, HealthProvider, TimeSlot, Vaccine, Booking
class BookingSerializer(serializers.ModelSerializer):
    child = serializers.PrimaryKeyRelatedField(queryset=Child.objects.all())
    health_provider = serializers.PrimaryKeyRelatedField(queryset=HealthProvider.objects.all())
    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
    vaccines = serializers.SerializerMethodField()  # Get vaccines based on age group

    class Meta:
        model = Booking
        fields = ['id', 'child', 'parent', 'health_provider', 'time_slot', 'status', 'vaccines', 'date', 'created_at', 'age_group']

    def get_vaccines(self, obj):
        """Auto-populate vaccines based on age group."""
        return list(Vaccine.objects.filter(age_group=obj.age_group).values_list('vaccine_name', flat=True))


class viewChildSerializer(serializers.ModelSerializer):
    parent = serializers.ReadOnlyField(source='parent.id')  # Read-only to prevent modification

    class Meta:
        model = Child
        fields = ['id', 'name', 'parent']

class HealthProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProvider
        fields = '__all__'


class AgeGroupStatusSerializer(serializers.Serializer):
    age_group = serializers.CharField()
    status = serializers.CharField()

class VaccinationHistorySerializer(serializers.Serializer):
    child_name = serializers.CharField()
    age_groups = AgeGroupStatusSerializer(many=True)