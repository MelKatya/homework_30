from datetime import datetime
from typing import List

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, NoResultFound

from .database import db
from .models import Client, ClientParking, Parking
from .utils import check_client_parking

app_route = Blueprint("routes", __name__)


@app_route.route("/clients", methods=["GET"])
def clients_get():
    """
    Выводит список всех клиентов.
    """
    clients: List[Client] = db.session.query(Client).all()
    clients_list = [u.to_json() for u in clients]
    return jsonify(clients_list)


@app_route.route("/clients/<int:client_id>", methods=["GET"])
def clients_get_id(client_id: int):
    """
    Выводит информацию о клиенте по ID.
    """
    try:
        client: Client = db.session.query(Client).filter(Client.id == client_id).one()
        return client.to_json()
    except NoResultFound:
        return jsonify(message=f"Client with id={client_id} not found"), 404


@app_route.route("/clients", methods=["POST"])
def clients_create():
    """
    Создает нового клиента.
    """
    name = request.form.get("name", type=str)
    surname = request.form.get("surname", type=str)
    credit_card = request.form.get("credit_card", type=str)
    car_number = request.form.get("car_number", type=str)

    try:
        new_client = Client(
            name=name, surname=surname, credit_card=credit_card, car_number=car_number
        )
        db.session.add(new_client)
        db.session.commit()
        return jsonify(message="Client created"), 201

    except IntegrityError as exc:
        return jsonify(error="Bad parameters", error_message=str(exc)), 400


@app_route.route("/parkings", methods=["POST"])
def parkings_create():
    """
    Создает новую парковочную зону.
    """
    fields = ("address", "opened", "count_places", "count_available_places")
    missing_fields = [field for field in fields if not request.form.get(field)]

    if missing_fields:
        return (
            jsonify(error=f'Missing required fields: {", ".join(missing_fields)}'),
            400,
        )

    address = request.form.get("address", type=str)
    opened_str = request.form.get("opened", type=str)
    count_places = request.form.get("count_places", type=int)
    count_available_places = request.form.get("count_available_places", type=int)

    opened = opened_str.lower() not in ["false", "0", "no"]

    if count_available_places > count_places:
        return (
            jsonify(
                error="The number of places must be greater than the number of available places"
            ),
            400,
        )

    try:
        new_parking = Parking(
            address=address,
            opened=opened,
            count_places=count_places,
            count_available_places=count_available_places,
        )
        db.session.add(new_parking)
        db.session.commit()
        return jsonify(messge="Parking created"), 201

    except IntegrityError as exc:
        return jsonify(error="Bad parameters", error_message=str(exc)), 400


@app_route.route("/client_parkings", methods=["POST"])
def client_parkings_create():
    """
    Выполняет заезд на парковку (проверяет, открыта ли парковка, количество свободных мест
    на парковке уменьшается, фиксируется дата заезда).
    """
    client_id = request.form.get("client_id", type=int)
    parking_id = request.form.get("parking_id", type=int)

    result_check = check_client_parking(client_id, parking_id)
    if result_check[1] == 404:
        return result_check

    client, parking = result_check

    if parking.count_available_places <= 0:
        return jsonify(message="There is no available places"), 400

    if not parking.opened:
        return jsonify(message="The parking is closed"), 400

    try:
        new_parking = ClientParking(
            client_id=client_id, parking_id=parking_id, time_in=datetime.utcnow()
        )
        parking.count_available_places -= 1
        db.session.add(new_parking)
        db.session.commit()
        return jsonify(message="Parking is occupied successfully")

    except IntegrityError:
        return jsonify(error="The client is already parked in this parking lot"), 400

    except Exception as exc:
        return jsonify(error="Something went wrong", error_message=str(exc)), 400


@app_route.route("/client_parkings", methods=["DELETE"])
def client_parkings_delete():
    """
    Выполняет выезд с парковки (количество свободных мест увеличивается, проставляется время выезда).
    """

    client_id = request.form.get("client_id", type=int)
    parking_id = request.form.get("parking_id", type=int)

    result_check = check_client_parking(client_id, parking_id)
    if result_check[1] == 404:
        return result_check

    client, parking = result_check

    client_parking = (
        db.session.query(ClientParking)
        .filter_by(client_id=client_id, parking_id=parking_id)
        .first()
    )
    if not client_parking:
        return (
            jsonify(
                error=f"The client with id={client_id} didn't park "
                f"in the parking lot with id={parking_id}"
            ),
            404,
        )

    if not client.credit_card:
        return (
            jsonify(
                message="You don't have a bank card linked to you. "
                "You're our hostage now"
            ),
            400,
        )

    if client_parking.time_out:
        return (
            jsonify(
                message="You've already left this parking lot. "
                "Drive away from another parking lot"
            ),
            400,
        )

    client_parking.time_out = datetime.utcnow()

    if client_parking.time_out < client_parking.time_in:
        return (
            jsonify(
                critical_error="You have broken the space-time continuum. "
                "Please don't do this anymore"
            ),
            409,
        )

    time_paring = client_parking.time_out - client_parking.time_in
    # Оплата поминутная
    payment = time_paring.total_seconds() // 60 * 10

    parking.count_available_places += 1
    db.session.commit()

    return jsonify(
        message="Thanks for visiting. Park with us again",
        payment=f"{payment} of the money will be debited during the parking period {time_paring}",
    )
