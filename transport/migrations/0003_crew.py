# Generated by Django 4.1 on 2025-03-30 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "transport",
            "0002_alter_train_cargo_num_alter_train_places_in_cargo_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Crew",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
            ],
        ),
    ]
