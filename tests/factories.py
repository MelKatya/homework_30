import factory
import random
from main.database import db as _db
from main.models import Client, Parking


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = _db.session

    name = factory.Faker('first_name')
    surname = factory.Faker('last_name')
    credit_card = factory.Faker('random_element', elements=[factory.Faker('credit_card_number'), None])
    car_number = factory.Faker('sentence')


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = _db.session

    address = factory.Faker('address')
    opened = factory.Faker('pybool')
    count_places = factory.Faker('pyint')
    count_available_places = factory.LazyAttribute(lambda o: abs(o.count_places -
                                                                 random.randint(1, 10)) % o.count_places)
