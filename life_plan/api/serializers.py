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
    items_for_plan = serializers.JSONField(write_only=True, required=False)
    years = serializers.ListField(
        child=serializers.IntegerField(min_value=1900),
        required=False
    )
    items = LifePlanItemSerializer(many=True, read_only=True)
    total_per_category = serializers.SerializerMethodField()
    profit_loss_by_date = serializers.SerializerMethodField()

    class Meta:
        model = LifePlan
        fields = [
            'id', 'user', 'name', 'created_at', 'updated_at', 'items_for_plan', 'years', 'items',
            'total_per_category', 'profit_loss_by_date'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'items', 'total_per_category', 'profit_loss_by_date']

    def get_total_per_category(self, obj):
        totals = defaultdict(Decimal)
        for item in obj.items.all():
            totals[item.category] += Decimal(item.value)
        return {category: float(total) for category, total in totals.items()}

    def get_profit_loss_by_date(self, obj):
        profit_loss_by_date = defaultdict(Decimal)
        receitas_by_date = defaultdict(Decimal)
        renda_extra_by_date = defaultdict(Decimal)
        custos_by_date = defaultdict(Decimal)

        for item in obj.items.all():
            if item.category == "receitas":
                receitas_by_date[item.date] += Decimal(item.value)
            elif item.category == "renda_extra":
                renda_extra_by_date[item.date] += Decimal(item.value)
            elif item.category in ["estudos", "custos"]:
                custos_by_date[item.date] += Decimal(item.value)

        all_dates = set(list(receitas_by_date.keys()) +
                    list(renda_extra_by_date.keys()) +
                    list(custos_by_date.keys()))

        for date in all_dates:
            profit_loss_by_date[date] = (
                receitas_by_date.get(date, Decimal(0)) +
                renda_extra_by_date.get(date, Decimal(0)) -
                custos_by_date.get(date, Decimal(0))
            )

        return [{"date": date, "profit_loss": float(value)} for date, value in profit_loss_by_date.items()]

    def create_default_items(self, life_plan, years):
        """Cria itens padrão para cada mês de cada ano especificado."""
        default_items = {
            'investimentos': [
                "Reserva Inicial", "Poupança", "Investimentos Planos",
                "Investimentos Planos", "Investimentos Planos", "Poupança Interâmbio"
            ],
            'empresas': ["Comprar Empresas", "Criar Empresas"],
            'realizacoes': [
                "Reforma no Apartamento", "Casamento", "Novo Apartamento",
                "Carro Novo", "Filhos", "Casa na Praia"
            ],
            'renda_extra': ["Aluguel", "Dividendos", "Venda de Produtos", "Plataforma"],
        }

        for year in years:
            for month in range(1, 13):
                for category, item_names in default_items.items():
                    for name in item_names:
                        LifePlanItem.objects.create(
                            life_plan=life_plan,
                            category=category,
                            name=name,
                            value=0,
                            date=datetime.strptime(f"{year}-{month:02d}-01", "%Y-%m-%d").date(),
                            meta=0
                        )

    def create(self, validated_data):
        """Criação de um LifePlan e seus itens padrão."""
        items_for_plan = validated_data.pop('items_for_plan', None)
        years = validated_data.pop('years', None)

        if not years:
            current_year = datetime.now().year
            years = [current_year]

        life_plan = LifePlan.objects.create(**validated_data)

        if not items_for_plan:
            self.create_default_items(life_plan, years)
        else:
            for category_name, category_data in items_for_plan.items():
                for item_data in category_data['items']:
                    LifePlanItem.objects.create(
                        life_plan=life_plan,
                        category=category_name,
                        name=item_data['name'],
                        value=item_data['value'],
                        date=datetime.strptime(item_data['date'], "%Y-%m-%d").date(),
                        meta=item_data.get('meta', 0) or 0
                    )

        return life_plan

    def update(self, instance, validated_data):
        """Atualizar um LifePlan e seus itens."""
        items_for_plan = validated_data.pop('items_for_plan', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        if items_for_plan:
            instance.items.all().delete()

            for category_name, category_data in items_for_plan.items():
                for item_data in category_data['items']:
                    LifePlanItem.objects.create(
                        life_plan=instance,
                        category=category_name,
                        name=item_data['name'],
                        value=item_data['value'],
                        date=datetime.strptime(item_data['date'], "%Y-%m-%d").date(),
                        meta=item_data.get('meta', 0) or 0
                    )

        return instance
