from rest_framework import serializers
from core.models.client import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'id', 'name', 'company_name', 'email', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'tax_id', 'currency', 'hourly_rate', 'payment_terms_days',
            'trust_score', 'notes', 'metadata',
            'is_active', 'archived_at', 'created_at', 'updated_at'
        ]


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'name', 'company_name', 'email', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'tax_id', 'currency', 'hourly_rate', 'payment_terms_days',
            'trust_score', 'notes', 'metadata'
        ]

    def validate_currency(self, value):
        if value and len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-letter code.")
        return value.upper() if value else value


class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            'name', 'company_name', 'email', 'phone',
            'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
            'tax_id', 'currency', 'hourly_rate', 'payment_terms_days',
            'trust_score', 'notes', 'metadata', 'is_active'
        ]

    def validate_currency(self, value):
        if value and len(value) != 3:
            raise serializers.ValidationError("Currency must be a 3-letter code.")
        return value.upper() if value else value
