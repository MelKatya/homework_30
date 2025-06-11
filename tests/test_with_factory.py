from main.models import Client, Parking
from tests.factories import ClientFactory, ParkingFactory


def test_create_user(app, db):
    client = ClientFactory()
    print(client.to_json())
    db.session.commit()
    assert client.id is not None
    assert len(db.session.query(Client).all()) == 2


def test_create_parking(app, db):
    product = ParkingFactory()
    db.session.commit()
    assert product.id is not None
    assert len(db.session.query(Parking).all()) == 2
