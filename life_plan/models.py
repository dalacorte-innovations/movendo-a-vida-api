from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime

class LifePlan(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="life_plans",
        verbose_name="User"
    )
    name = models.CharField(max_length=100, verbose_name="Name of Life Plan")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def __str__(self):
        return f"Life Plan for {self.user.email}"

    @classmethod
    def create_default_plan(cls, user, name="Meu Plano de Vida"):
        """
        Cria um plano de vida padrão para o usuário com itens pré-definidos para 1 ano
        apenas se o usuário ainda não tiver um plano
        """
        existing_plan = cls.objects.filter(user=user, name=name).first()
        if existing_plan:
            return existing_plan

        plan = cls.objects.create(
        user=user,
        name=name
        )

        current_year = datetime.now().year

        default_items = {
            'receitas': [
                {"name": "Salário", "value": 5000.00, "meta": 5000.00},
                {"name": "Freelance", "value": 1000.00, "meta": 1000.00},
                {"name": "Outras Receitas", "value": 500.00, "meta": 500.00},
            ],
            'custos': [
                {"name": "Moradia", "value": 1800.00, "meta": 1800.00},
                {"name": "Alimentação", "value": 1200.00, "meta": 1200.00},
                {"name": "Transporte", "value": 600.00, "meta": 600.00},
                {"name": "Saúde", "value": 400.00, "meta": 400.00},
                {"name": "Lazer", "value": 500.00, "meta": 500.00},
                {"name": "Serviços", "value": 450.00, "meta": 450.00},
            ],
            'estudos': [
                {"name": "Curso de Especialização", "value": 500.00, "meta": 6000.00},
                {"name": "Idiomas", "value": 200.00, "meta": 2400.00},
                {"name": "Livros/Material", "value": 100.00, "meta": 1200.00},
            ],
            'investimentos': [
                {"name": "Reserva de Emergência", "value": 500.00, "meta": 6000.00},
                {"name": "Renda Fixa", "value": 150.00, "meta": 1800.00},
                {"name": "Renda Variável", "value": 100.00, "meta": 1200.00},
            ],
            'realizacoes': [
                {"name": "Viagem Nacional", "value": 3000.00, "meta": 3000.00, "month": 7},
                {"name": "Compra de Notebook", "value": 5000.00, "meta": 5000.00, "month": 10},
                {"name": "Reforma do Quarto", "value": 2500.00, "meta": 2500.00, "month": 12},
            ],
            'intercambio': [
                {"name": "Poupança para Intercâmbio", "value": 1000.00, "meta": 12000.00},
            ],
            'empresas': [
                {"name": "Projeto Freelance", "value": 2000.00, "meta": 5000.00, "month": 6},
                {"name": "Startup Tecnologia", "value": 10000.00, "meta": 50000.00, "month": 3},
                {"name": "E-commerce", "value": 5000.00, "meta": 20000.00, "month": 9},
                {"name": "Consultoria", "value": 1500.00, "meta": 15000.00, "month": 1},
                {"name": "Curso Online", "value": 3000.00, "meta": 12000.00, "month": 4},
            ],
            'pessoais': [
                {"name": "Desenvolvimento Pessoal", "value": 200.00, "meta": 2400.00},
                {"name": "Terapia", "value": 300.00, "meta": 3600.00},
                {"name": "Atividade Física", "value": 150.00, "meta": 1800.00},
                {"name": "Hobby", "value": 100.00, "meta": 1200.00},
                {"name": "Voluntariado", "value": 50.00, "meta": 600.00},
            ],
        }

        for month in range(1, 13):
            date = datetime(current_year, month, 1).date()

            for category in ['receitas', 'custos', 'estudos', 'investimentos', 'intercambio', 'pessoais']:
                for item in default_items.get(category, []):
                    LifePlanItem.objects.create(
                        life_plan=plan,
                        category=category,
                        name=item["name"],
                        value=item["value"],
                        date=date,
                        meta=item["meta"]
                    )

            for item in default_items.get('realizacoes', []):
                if item.get("month") == month:
                    LifePlanItem.objects.create(
                        life_plan=plan,
                        category='realizacoes',
                        name=item["name"],
                        value=item["value"],
                        date=date,
                        meta=item["meta"]
                    )

            for item in default_items.get('empresas', []):
                if item.get("month") == month:
                    LifePlanItem.objects.create(
                        life_plan=plan,
                        category='empresas',
                        name=item["name"],
                        value=item["value"],
                        date=date,
                        meta=item["meta"]
                    )

            receitas_total = sum(item["value"] for item in default_items.get('receitas', []))
            custos_total = sum(item["value"] for item in default_items.get('custos', []))
            estudos_total = sum(item["value"] for item in default_items.get('estudos', []))
            lucro = receitas_total - (custos_total + estudos_total)

            LifePlanItem.objects.create(
                life_plan=plan,
                category='lucro_prejuizo',
                name="Lucro/Prejuízo Mensal",
                value=lucro,
                date=date,
                meta=lucro
            )

        return plan

class LifePlanItem(models.Model):
    CATEGORY_CHOICES = [
        ('receitas', _("Receitas")),
        ('estudos', _("Estudos")),
        ('custos', _("Custos")),
        ('lucro_prejuizo', _("Lucro/Prejuízo")),
        ('investimentos', _("Investimentos")),
        ('realizacoes', _("Realizações")),
        ('intercambio', _("Intercâmbio")),
        ('empresas', _("Empresas")),
    ]

    life_plan = models.ForeignKey(
        LifePlan,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Life Plan"
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="Category")
    name = models.CharField(max_length=100, verbose_name="Item Name")
    value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Value")
    date = models.DateField(verbose_name="Date")
    meta = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Meta")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    def __str__(self):
        return f"{self.category} - {self.name}: {self.value}"