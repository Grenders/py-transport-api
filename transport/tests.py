from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Station, Route, Crew, TrainType, Train, Journey, Order, Ticket
import datetime


class StationModelTest(TestCase):
    def test_create_station(self):
        station = Station.objects.create(
            name="Central", latitude=40.7128, longitude=-74.0060
        )
        self.assertEqual(station.name, "Central")
        self.assertEqual(station.latitude, 40.7128)
        self.assertEqual(station.longitude, -74.0060)
        self.assertEqual(
            str(station), "Station: Central (latitude: 40.7128, longitude: -74.006)"
        )

    def test_latitude_validation(self):
        with self.assertRaises(ValidationError):
            station = Station(name="Invalid", latitude=100, longitude=0)
            station.full_clean()

    def test_longitude_validation(self):
        with self.assertRaises(ValidationError):
            station = Station(name="Invalid", latitude=0, longitude=200)
            station.full_clean()

    def test_unique_name(self):
        Station.objects.create(name="Unique", latitude=0, longitude=0)
        with self.assertRaises(ValidationError):
            duplicate = Station(name="Unique", latitude=1, longitude=1)
            duplicate.full_clean()


class RouteModelTest(TestCase):
    def setUp(self):
        self.station1 = Station.objects.create(
            name="Station A", latitude=0, longitude=0
        )
        self.station2 = Station.objects.create(
            name="Station B", latitude=1, longitude=1
        )

    def test_create_route(self):
        route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=100
        )
        self.assertEqual(route.source, self.station1)
        self.assertEqual(route.destination, self.station2)
        self.assertEqual(route.distance, 100)
        self.assertEqual(str(route), "100 - Station A")

    def test_unique_together(self):
        Route.objects.create(
            source=self.station1, destination=self.station2, distance=100
        )
        with self.assertRaises(ValidationError):
            duplicate = Route(
                source=self.station1, destination=self.station2, distance=200
            )
            duplicate.full_clean()

    def test_distance_validation(self):
        with self.assertRaises(ValidationError):
            route = Route(source=self.station1, destination=self.station2, distance=-1)
            route.full_clean()


class CrewModelTest(TestCase):
    def test_create_crew(self):
        crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.assertEqual(crew.first_name, "John")
        self.assertEqual(crew.last_name, "Doe")
        self.assertEqual(crew.full_name, "John Doe")
        self.assertEqual(str(crew), "Crew - John Doe")


class TrainTypeModelTest(TestCase):
    def test_create_train_type(self):
        train_type = TrainType.objects.create(name="Express")
        self.assertEqual(train_type.name, "Express")
        self.assertEqual(str(train_type), "Express")

    def test_unique_name(self):
        TrainType.objects.create(name="Express")
        with self.assertRaises(ValidationError):
            duplicate = TrainType(name="Express")
            duplicate.full_clean()


class TrainModelTest(TestCase):
    def setUp(self):
        self.train_type = TrainType.objects.create(name="Freight")

    def test_create_train(self):
        train = Train.objects.create(
            name="Thunderbolt",
            cargo_num=50,
            places_in_cargo=20,
            train_type=self.train_type,
        )
        self.assertEqual(train.name, "Thunderbolt")
        self.assertEqual(train.cargo_num, 50)
        self.assertEqual(train.places_in_cargo, 20)
        self.assertEqual(str(train), "Thunderbolt (50 20)")

    def test_cargo_validation(self):
        with self.assertRaises(ValidationError):
            train = Train(
                name="Invalid",
                cargo_num=101,
                places_in_cargo=20,
                train_type=self.train_type,
            )
            train.full_clean()

    def test_places_validation(self):
        with self.assertRaises(ValidationError):
            train = Train(
                name="Invalid",
                cargo_num=50,
                places_in_cargo=-1,
                train_type=self.train_type,
            )
            train.full_clean()


class JourneyModelTest(TestCase):
    def setUp(self):
        self.station1 = Station.objects.create(
            name="Station A", latitude=0, longitude=0
        )
        self.station2 = Station.objects.create(
            name="Station B", latitude=1, longitude=1
        )
        self.route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=100
        )
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Thunderbolt",
            cargo_num=50,
            places_in_cargo=20,
            train_type=self.train_type,
        )
        self.crew = Crew.objects.create(first_name="John", last_name="Doe")

    def test_create_journey(self):
        departure = timezone.now() + datetime.timedelta(hours=1)
        arrival = departure + datetime.timedelta(hours=2)
        journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=departure,
            arrival_time=arrival,
        )
        journey.crew.add(self.crew)
        self.assertEqual(journey.route, self.route)
        self.assertEqual(journey.train, self.train)
        self.assertEqual(
            str(journey),
            f"Journey on route from Station A to Station B by train Thunderbolt",
        )

    def test_departure_time_in_past(self):
        departure = timezone.now() - datetime.timedelta(hours=1)
        arrival = departure + datetime.timedelta(hours=2)
        journey = Journey(
            route=self.route,
            train=self.train,
            departure_time=departure,
            arrival_time=arrival,
        )
        with self.assertRaises(ValidationError):
            journey.full_clean()

    def test_arrival_before_departure(self):
        departure = timezone.now() + datetime.timedelta(hours=2)
        arrival = departure - datetime.timedelta(hours=1)
        journey = Journey(
            route=self.route,
            train=self.train,
            departure_time=departure,
            arrival_time=arrival,
        )
        with self.assertRaises(ValidationError):
            journey.full_clean()


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpass",
            first_name="Test",
            last_name="User",
        )

    def test_create_order(self):
        order = Order.objects.create(user=self.user)
        self.assertEqual(order.user, self.user)
        self.assertTrue(order.created_at)
        self.assertEqual(str(order), str(order.created_at))

    def test_ordering(self):
        order1 = Order.objects.create(user=self.user)
        order2 = Order.objects.create(user=self.user)
        orders = Order.objects.all()
        self.assertEqual(orders[0], order2)
        self.assertEqual(orders[1], order1)


class TicketModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="testpass",
            first_name="Test",
            last_name="User",
        )
        self.station1 = Station.objects.create(
            name="Station A", latitude=0, longitude=0
        )
        self.station2 = Station.objects.create(
            name="Station B", latitude=1, longitude=1
        )
        self.route = Route.objects.create(
            source=self.station1, destination=self.station2, distance=100
        )
        self.train_type = TrainType.objects.create(name="Express")
        self.train = Train.objects.create(
            name="Thunderbolt",
            cargo_num=50,
            places_in_cargo=20,
            train_type=self.train_type,
        )
        departure = timezone.now() + datetime.timedelta(hours=1)
        arrival = departure + datetime.timedelta(hours=2)
        self.journey = Journey.objects.create(
            route=self.route,
            train=self.train,
            departure_time=departure,
            arrival_time=arrival,
        )
        self.order = Order.objects.create(user=self.user)

    def test_create_ticket(self):
        ticket = Ticket.objects.create(
            cargo=1, seat=1, journey=self.journey, order=self.order
        )
        self.assertEqual(ticket.cargo, 1)
        self.assertEqual(ticket.seat, 1)
        self.assertEqual(
            str(ticket), f"Journey ID {self.journey.id} (cargo: 1, seat: 1)"
        )

    def test_unique_together(self):
        Ticket.objects.create(cargo=1, seat=1, journey=self.journey, order=self.order)
        with self.assertRaises(ValidationError):
            duplicate = Ticket(cargo=1, seat=1, journey=self.journey, order=self.order)
            duplicate.full_clean()

    def test_cargo_validation(self):
        ticket = Ticket(cargo=51, seat=1, journey=self.journey, order=self.order)
        with self.assertRaises(ValidationError):
            ticket.full_clean()

    def test_seat_validation(self):
        ticket = Ticket(cargo=1, seat=21, journey=self.journey, order=self.order)
        with self.assertRaises(ValidationError):
            ticket.full_clean()
