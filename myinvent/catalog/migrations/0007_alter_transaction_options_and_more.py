# Generated by Django 5.1.2 on 2024-11-23 01:01

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0006_productionorder"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="transaction",
            options={"ordering": ["-date"]},
        ),
        migrations.RemoveField(
            model_name="transaction",
            name="transaction_date",
        ),
        migrations.AddField(
            model_name="transaction",
            name="date",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="transaction",
            name="notes",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="quantity",
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="transaction_type",
            field=models.CharField(
                choices=[("IN", "Stock In"), ("OUT", "Stock Out")], max_length=3
            ),
        ),
    ]
