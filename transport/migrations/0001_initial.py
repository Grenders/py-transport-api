# Generated by Django 4.1 on 2025-03-30 14:57

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Station",
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
                ("name", models.CharField(max_length=255, unique=True)),
                (
                    "latitude",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(-90.0),
                            django.core.validators.MaxValueValidator(90.0),
                        ]
                    ),
                ),
                (
                    "longitude",
                    models.FloatField(
                        validators=[
                            django.core.validators.MinValueValidator(-180),
                            django.core.validators.MaxValueValidator(180.0),
                        ]
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "stations",
            },
        ),
        migrations.CreateModel(
            name="TrainType",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Train",
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
                ("name", models.CharField(max_length=255)),
                (
                    "cargo_num",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(0)]
                    ),
                ),
                (
                    "places_in_cargo",
                    models.IntegerField(
                        validators=[django.core.validators.MinValueValidator(0)]
                    ),
                ),
                (
                    "train_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="transport.traintype",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "trains",
            },
        ),
    ]
