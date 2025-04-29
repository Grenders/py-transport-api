from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180.0)]
    )

    class Meta:
        verbose_name_plural = "stations"

    def __str__(self) -> str:
        return f"Station: {self.name} (latitude: {self.latitude}, longitude: {self.longitude})"


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="destination_routes"
    )
    distance = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        verbose_name_plural = "routes"
        unique_together = ("source", "destination")

    def __str__(self) -> str:
        return f"{self.distance} - {self.source.name}"


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self) -> str:
        return f"Crew - {self.first_name} {self.last_name}"


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return f"{self.name}"


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    places_in_cargo = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "trains"

    def __str__(self) -> str:
        return f"{self.name} ({self.cargo_num} {self.places_in_cargo})"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journeys")

    def clean(self):
        if self.departure_time < timezone.now():
            raise ValidationError(
                {"departure_time": "Departure time cannot be in the past."}
            )

        if self.arrival_time < self.departure_time:
            raise ValidationError(
                {"arrival_time": "Arrival time cannot be earlier than departure time."}
            )

        super().clean()

    def save(self, *args, **kwargs):
        if self.pk and self.departure_time < timezone.now():
            raise ValidationError("Cannot update a journey that has already started.")
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"Journey on route from {self.route.source.name} to {self.route.destination.name} by train {self.train.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    cargo = models.IntegerField(validators=[MinValueValidator(0)])
    seat = models.IntegerField(validators=[MinValueValidator(0)])
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    @staticmethod
    def validate_ticket(cargo, seat, journey, error_to_raise):
        for ticket_attr_value, ticket_attr_name, train_attr_name in [
            (cargo, "row", "cargo_num"),
            (seat, "seat", "places_in_cargo"),
        ]:
            count_attrs = getattr(journey, train_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_name} "
                        f"number must be in available range: "
                        f"(1, {train_attr_name}): "
                        f"(1, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.cargo,
            self.seat,
            self.journey.train,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
        **kwargs,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self) -> str:
        return f"Journey ID {self.journey.id} (cargo: {self.cargo}, seat: {self.seat})"

    class Meta:
        unique_together = ("journey", "cargo", "seat")
        ordering = ["cargo", "seat"]
