# Generated by Django 5.1.1 on 2024-10-20 23:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        ('users', '0003_user_plan_name_user_stripe_customer_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='plan_name',
        ),
        migrations.RemoveField(
            model_name='user',
            name='restricted_access',
        ),
        migrations.RemoveField(
            model_name='user',
            name='user_free',
        ),
        migrations.AddField(
            model_name='user',
            name='plan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='payments.product', verbose_name='Current Plan'),
        ),
        migrations.AlterField(
            model_name='user',
            name='payment_made',
            field=models.BooleanField(default=False, verbose_name='Payment made'),
        ),
    ]
