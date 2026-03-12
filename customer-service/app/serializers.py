from rest_framework import serializers
from .models import Customer, Address, Job

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'password', 'address', 'job', 'cart_id']
        extra_kwargs = {'password': {'write_only': True}}
        
    def create(self, validated_data):
        user = Customer.objects.create_user(**validated_data)
        return user