from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from transport.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Journey,
    Ticket,
    Order,
)


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(TrainSerializer):
    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainDetailSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(read_only=True)

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteListSerializer(RouteSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class CrewSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")

    @extend_schema_field(serializers.CharField)
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")

    def validate(self, data):
        departure = data.get("departure_time")
        arrival = data.get("arrival_time")

        if departure and arrival and arrival < departure:
            raise serializers.ValidationError(
                {"arrival_time": "arrival time not be higher departure time"}
            )
        return data


class JourneyListSerializer(JourneySerializer):
    route = RouteSerializer(many=False, read_only=True)
    train = TrainSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class JourneyDetailSerializer(JourneySerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    train = TrainDetailSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "crew")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"], attrs["seat"], attrs["journey"].train, ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class TicketListSerializer(TicketSerializer):
    journey = JourneyListSerializer(many=False, read_only=True)


class TicketSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(
        many=True, read_only=False, allow_empty=False, source="ticket_set"
    )

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at", "user")
        read_only_fields = ("user", "created_at")

    def create(self, validated_data):
        tickets_data = validated_data.pop("ticket_set")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True, source="ticket_set")

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at", "user")
        read_only_fields = ("user", "created_at")
