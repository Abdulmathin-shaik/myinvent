# Generated by Django 5.1.2 on 2024-11-23 02:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0008_alter_billofmaterials_name_alter_bomitem_bom"),
    ]

    operations = [
        migrations.AddField(
            model_name="rawmaterial",
            name="barcode",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
