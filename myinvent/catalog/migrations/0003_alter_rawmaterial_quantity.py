# Generated by Django 5.1.2 on 2024-11-17 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0002_alter_rawmaterial_sku"),
    ]

    operations = [
        migrations.AlterField(
            model_name="rawmaterial",
            name="quantity",
            field=models.IntegerField(),
        ),
    ]