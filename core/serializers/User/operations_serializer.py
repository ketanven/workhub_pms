from rest_framework import serializers
from core.models.operations import (
    ReportExport,
    ProductivityRuleConfig,
    ProductivityScore,
    ClientTrustRuleConfig,
    ClientTrustScore,
    ClientRiskAlert,
)


class ReportExportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = ['report_type', 'period_type', 'filters_json', 'file_format']


class ReportExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportExport
        fields = '__all__'


class ProductivityRuleConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductivityRuleConfig
        fields = '__all__'


class ProductivityScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductivityScore
        fields = '__all__'


class ClientTrustRuleConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientTrustRuleConfig
        fields = '__all__'


class ClientTrustScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientTrustScore
        fields = '__all__'


class ClientRiskAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientRiskAlert
        fields = '__all__'
