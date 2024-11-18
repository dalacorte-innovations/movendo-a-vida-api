from rest_framework import serializers
from life_plan.models import LifePlan, LifePlanItem
from datetime import datetime
from collections import defaultdict
from decimal import Decimal

class LifePlanItemSerializer(serializers.ModelSerializer):
    date = serializers.DateField()

    class Meta:
        model = LifePlanItem
        fields = ['category', 'name', 'value', 'date', 'meta']

class LifePlanSerializer(serializers.ModelSerializer):
    items_for_plan = serializers.JSONField(write_only=True)
    items = LifePlanItemSerializer(many=True, read_only=True)
    total_per_category = serializers.SerializerMethodField()
    profit_loss_by_date = serializers.SerializerMethodField()

    class Meta:
        model = LifePlan
        fields = ['id', 'user', 'name', 'created_at', 'updated_at', 'items_for_plan', 'items', 'total_per_category', 'profit_loss_by_date']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'items', 'total_per_category', 'profit_loss_by_date']

    def get_total_per_category(self, obj):
        totals = defaultdict(Decimal)
        for item in obj.items.all():
            totals[item.category] += Decimal(item.value)
        return {category: float(total) for category, total in totals.items()}

    def get_profit_loss_by_date(self, obj):
        profit_loss_by_date = defaultdict(Decimal)

        receitas_by_date = defaultdict(Decimal)
        custos_by_date = defaultdict(Decimal)

        for item in obj.items.all():
            if item.category == "receitas":
                receitas_by_date[item.date] += Decimal(item.value)
            elif item.category in ["estudos", "custos"]:
                custos_by_date[item.date] += Decimal(item.value)

        for date in receitas_by_date:
            profit_loss_by_date[date] = receitas_by_date[date] - custos_by_date.get(date, Decimal(0))

        return [{"date": date, "profit_loss": float(value)} for date, value in profit_loss_by_date.items()]

    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return datetime.strptime(date_str, '%d;%m;%Y').date()

    def create(self, validated_data):
        items_data = validated_data.pop('items_for_plan', {})
        life_plan = LifePlan.objects.create(**validated_data)

        for category_name, category_data in items_data.items():
            for item_data in category_data['items']:
                LifePlanItem.objects.create(
                    life_plan=life_plan,
                    category=category_name,
                    name=item_data['name'],
                    value=item_data['value'],
                    date=self.parse_date(item_data['date']),
                    meta=item_data.get('meta', 0) or 0
                )

        return life_plan

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items_for_plan', {})
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        instance.items.all().delete()
        for category_name, category_data in items_data.items():
            for item_data in category_data['items']:
                LifePlanItem.objects.create(
                    life_plan=instance,
                    category=category_name,
                    name=item_data['name'],
                    value=item_data['value'],
                    date=self.parse_date(item_data['date']),
                    meta=item_data.get('meta', 0) or 0
                )

        return instance
