from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication

from transport.models import (
    Station,
    TrainType,
    Train,
    Route,
    Crew,
    Journey,
    Order,
)
from transport.serializers import (
    TrainListSerializer,
    TrainDetailSerializer,
    StationSerializer,
    TrainTypeSerializer,
    RouteSerializer,
    CrewSerializer,
    JourneySerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    OrderSerializer,
    OrderListSerializer,
)


class StationViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Station.objects.all().order_by("id")
    serializer_class = StationSerializer
    pagination_class = PageNumberPagination
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)


class TrainTypeViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = TrainType.objects.all().order_by("id")
    serializer_class = TrainTypeSerializer
    pagination_class = PageNumberPagination
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.select_related("train_type").order_by("id")
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the trains with filters"""
        name = self.request.query_params.get("name")
        train_types = self.request.query_params.get("train_types")
        cargo_num = self.request.query_params.get("cargo_num")
        places_in_cargo = self.request.query_params.get("places_in_cargo")

        queryset = self.queryset

        if name:
            queryset = queryset.filter(name__icontains=name)

        if cargo_num and cargo_num.isdigit():
            queryset = queryset.filter(cargo_num=cargo_num)

        if places_in_cargo and places_in_cargo.isdigit():
            queryset = queryset.filter(places_in_cargo=places_in_cargo)

        if train_types:
            train_type_ids = self._params_to_ints(train_types)
            queryset = queryset.filter(train_type__id__in=train_type_ids)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type=OpenApiTypes.STR,
                description="Filter by train name (ex. ?name=train1)",
            ),
            OpenApiParameter(
                "train_types",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by train_types id (ex. ?train_types=2,5)",
            ),
            OpenApiParameter(
                "cargo_num",
                type=OpenApiTypes.INT,
                description="Filter by number of cargo (ex. ?cargo_num=10)",
            ),
            OpenApiParameter(
                "places_in_cargo",
                type=OpenApiTypes.INT,
                description="Filter by places in cargo (ex. ?places_in_cargo=50)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainDetailSerializer
        return TrainListSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = (
        Route.objects.all().select_related("source", "destination").order_by("id")
    )
    serializer_class = RouteSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all().order_by("id")
    serializer_class = CrewSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.all()
        .select_related("route", "train")
        .prefetch_related("crew")
        .order_by("id")
    )
    serializer_class = JourneySerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    @staticmethod
    def _params_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve the Journey with filters"""
        route = self.request.query_params.get("route")
        train = self.request.query_params.get("train")
        crew = self.request.query_params.get("crew")
        departure_after = self.request.query_params.get("departure_after")
        arrival_before = self.request.query_params.get("arrival_before")

        queryset = self.queryset

        if route:
            route_id = self._params_to_ints(route)
            queryset = queryset.filter(route__id__in=route_id)
        if train:
            train_id = self._params_to_ints(train)
            queryset = queryset.filter(train__id__in=train_id)
        if crew:
            crew_id = self._params_to_ints(crew)
            queryset = queryset.filter(crew__id__in=crew_id)
        if departure_after:
            queryset = queryset.filter(departure_time__gte=departure_after)
        if arrival_before:
            queryset = queryset.filter(arrival_time__lte=arrival_before)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "route",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by route id (ex. ?route=2,5)",
            ),
            OpenApiParameter(
                "train",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by train id (ex. ?train=2,5)",
            ),
            OpenApiParameter(
                "crew",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by crew id (ex. ?crew=2,5)",
            ),
            OpenApiParameter(
                "departure_after",
                type=OpenApiTypes.DATETIME,
                description="Filter journeys departing after this time (ex. ?departure_after=2025-04-24T10:00:00Z)",
            ),
            OpenApiParameter(
                "arrival_before",
                type=OpenApiTypes.DATETIME,
                description="Filter journeys arriving before this time (ex. ?arrival_before=2025-04-24T18:00:00Z)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        if self.action == "retrieve":
            return JourneyDetailSerializer
        return JourneySerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    queryset = Order.objects.prefetch_related(
        "tickets__journey__route", "tickets__journey__train"
    ).order_by("-created_at")
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
