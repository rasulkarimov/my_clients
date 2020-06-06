from rest_framework import serializers
from .models import *


class ActivityDirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityDirection
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    activity_direction = ActivityDirectionSerializer(many=False, read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = '__all__'


class CallSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(many=False, read_only=True)

    class Meta:
        model = Calls
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(many=False, read_only=True)

    class Meta:
        model = Orders
        fields = '__all__'


class InformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Information
        fields = '__all__'


