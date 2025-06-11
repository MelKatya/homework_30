from datetime import datetime
from typing import Literal

from .database import db
from .models import Client, ClientParking, Parking


def get_all_client():
    all_client = db.session.query(Client).all()
    return [row.to_json() for row in all_client]


def add_client(client: Client) -> Client:
    db.session.add(client)
    db.session.commit()
    return client


def get_client_by_id(client_id: int):
    return db.session.query(Client).\
        filter(Client.id == client_id).one_or_none()


def get_all_parkings():
    all_client = db.session.query(Parking).all()
    return [row.to_json() for row in all_client]


def add_parking(parking: Parking) -> Parking:
    db.session.add(parking)
    db.session.commit()
    return parking


def check_client_exists(client_id: int) -> bool:
    return db.session.query(Client).where(Client.id == client_id).one_or_none()


def check_parking_exists(parking_id: int) -> bool:
    return db.session.query(Parking).\
        where(Parking.id == parking_id).one_or_none()


def check_parking_open(parking_id: int) -> bool:
    parking = db.session.query(Parking)\
        .where(Parking.id == parking_id).one()
    return parking.opened


def get_all_client_parkings():
    all_client_parkings = db.session.query(ClientParking).all()
    return [row.to_json() for row in all_client_parkings]


def change_available_places(parking_id: int, delta: Literal[-1, 1]) -> bool:
    parking = db.session.query(Parking).where(Parking.id == parking_id).one()
    if parking.count_available_places <= 0 and delta == -1:
        return False

    parking.count_available_places += delta
    return True


def add_client_parking(new_parking: ClientParking) -> ClientParking | None:
    if not change_available_places(new_parking.parking_id, -1):
        raise ArithmeticError
    new_parking.time_in = datetime.utcnow()
    db.session.add(new_parking)
    db.session.commit()
    return new_parking


def delete_client_parking(client_id: int, parking_id: int):
    client_parking = (
        db.session.query(ClientParking)
        .filter_by(client_id=client_id, parking_id=parking_id)
        .first()
    )

    if not client_parking:
        return None

    if not client_parking.client.credit_card:
        raise UserWarning

    if client_parking.time_out:
        raise KeyError

    client_parking.time_out = datetime.utcnow()
    change_available_places(parking_id, 1)

    time_paring = client_parking.time_out - client_parking.time_in
    # Оплата поминутная
    payment = time_paring.total_seconds() // 60 * 10
    db.session.commit()

    return payment
