import pytest
from main.app import create_app
from main.database import db as _db
from main.models import Client, Parking, ClientParking
from datetime import datetime, timedelta


@pytest.fixture
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with _app.app_context():
        _db.create_all()
        user = Client(name='Peter', surname='Ivanov', credit_card='6876 8989 66', car_number='FF0909F')
        product = Parking(address='address', opened=True,
                          count_places=5, count_available_places=2)

        client_parking = ClientParking(client_id=1, parking_id=1,
                                       time_in=datetime.utcnow(), time_out=datetime.utcnow() + timedelta(hours=2))

        _db.session.add(user)
        _db.session.add(product)
        _db.session.add(client_parking)
        _db.session.commit()

        yield _app
        _db.session.close()
        _db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
