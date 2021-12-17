from rest_framework import serializers
from api.models import User, Client, Contract, Event


class ClientSerializer(serializers.ModelSerializer):
    sale_contact = serializers.StringRelatedField()
    class Meta:
        model = Client
        fields = ['id', 'firstname', 'lastname', 'email', 'phone', 'mobile',
                  'role', 'company_name', 'date_created', 'date_updated', 'sale_contact']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'role', 'lastname']


class ContractSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    sales_contact = serializers.StringRelatedField()
    class Meta:
        model = Contract
        fields = ['id', 'date_created', 'date_updated', 'status', 'amount',
                  'payment_due', 'client', 'sales_contact']



class EventSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField()
    contract = serializers.StringRelatedField()
    support_contact = serializers.StringRelatedField()
    class Meta:
        model = Event
        fields = ['id', 'date_created', 'date_updated', 'attendees', 'event_date',
                  'notes', 'client', 'support_contact', 'contract']
