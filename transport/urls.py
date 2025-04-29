from django.urls import path, include
from rest_framework import routers


from transport.views import (
    StationViewSet,
    TrainTypeViewSet,
    TrainViewSet,
    RouteViewSet,
    CrewViewSet,
    JourneyViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("stations", StationViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("trains", TrainViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("journey", JourneyViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "transport"
