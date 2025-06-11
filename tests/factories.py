import random

import factory
from faker import Faker

from main.database import db as _db
from main.models import Client, Parking


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = _db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")

    credit_card = factory.LazyFunction(
        lambda: Faker().credit_card_number() if random.choice([True, False]) else None
    )
    car_number = factory.Faker("sentence")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = _db.session

    address = factory.Faker("address")
    opened = factory.Faker("pybool")
    count_places = factory.Faker("pyint")
    count_available_places = factory.LazyAttribute(
        lambda o: abs(o.count_places - random.randint(1, 10)) % o.count_places
    )
