from tests.factories import ClientFactory, ParkingFactory
from main.models import Client, Parking


def test_create_user(app, db):
    client = ClientFactory()
    db.session.commit()
    assert client.id is not None
    assert len(db.session.query(Client).all()) == 2


def test_create_product(app, db):
    product = ParkingFactory()
    db.session.commit()
    assert product.id is not None
    assert len(db.session.query(Parking).all()) == 2
