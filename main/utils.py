from flask import jsonify

from .database import db
from .models import Client, Parking


def check_client_parking(client_id: int, parking_id: int):
    """
    Проверяет существование ID клиента и парковки.
    """
    client = db.session.query(Client).filter(Client.id == client_id).all()
    parking = db.session.query(Parking).filter(Parking.id == parking_id).all()

    if not client:
        return jsonify(error=f"There is no client with id={client_id}"), 404

    if not parking:
        return jsonify(error=f"There is no parking with id={parking_id}"), 404

    return client[0], parking[0]
