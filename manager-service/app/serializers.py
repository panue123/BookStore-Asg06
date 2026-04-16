from rest_framework import serializers
from .models import Manager, InventoryLog, SalesReport


class ManagerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Manager
        fields = ['id', 'name', 'email', 'password', 'department', 'is_active', 'created_at']

    def create(self, validated_data):
        return Manager.objects.create(**validated_data)


class InventoryLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryLog
        fields = '__all__'


class SalesReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesReport
        fields = '__all__'
