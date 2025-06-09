from datetime import datetime, timedelta
import json
import pytest


def test_user(client) -> None:
    resp = client.get("/clients/1")
    assert resp.status_code == 200
    assert resp.json == {"id": 1,
                         "name": 'Peter',
                         "surname": 'Ivanov',
                         "credit_card": '6876 8989 66',
                         "car_number": 'FF0909F'}


def test_create_client(client) -> None:
    client_data = {"name": 'Peter2', "surname": 'Ivanov2', "credit_card": '6876 8989 66', "car_number": 'FF0909F'}
    resp = client.post("/clients", data=client_data)
    assert resp.status_code == 201


def test_create_client_without_name(client) -> None:
    client_data = {"surname": 'Ivanov2', "credit_card": '6876 8989 66', "car_number": 'FF0909F'}
    resp = client.post("/clients", data=client_data)
    assert resp.status_code == 400


def test_create_parkings(client) -> None:
    parking_data = {"address": 'address2', "opened": True, "count_places": 5, "count_available_places": 2}
    resp = client.post("/parkings", data=parking_data)
    assert resp.status_code == 201


def test_create_parkings_wrong_places(client) -> None:
    parking_data = {"address": 'address2', "opened": True, "count_places": 5, "count_available_places": 7}
    resp = client.post("/parkings", data=parking_data)
    assert resp.status_code == 400
    assert json.loads(resp.text) == \
           {"error": "The number of places must be greater than the number of available places"}


@pytest.mark.parking
def test_check_in(client) -> None:
    client_data = {"name": 'Peter2', "surname": 'Ivanov2', "credit_card": '6876 8989 66', "car_number": 'FF0909F'}
    client.post("/clients", data=client_data)

    parking_data = {"address": 'address2', "opened": True, "count_places": 5, "count_available_places": 2}
    client.post("/parkings", data=parking_data)

    check_in = {"client_id": 2, 'parking_id': 2, "time_in": datetime.utcnow()}
    resp = client.post("/client_parkings", data=check_in)
    assert resp.status_code == 200


@pytest.mark.parking
def test_check_in_parking_closed(client) -> None:
    client_data = {"name": 'Peter2', "surname": 'Ivanov2', "credit_card": '6876 8989 66', "car_number": 'FF0909F'}
    client.post("/clients", data=client_data)

    parking_data = {"address": 'address2', "opened": False, "count_places": 5, "count_available_places": 2}
    client.post("/parkings", data=parking_data)

    check_in = {"client_id": 2, 'parking_id': 2, "time_in": datetime.utcnow()}
    resp = client.post("/client_parkings", data=check_in)

    assert resp.status_code == 400
    assert json.loads(resp.text) == {"message": "The parking is closed"}


@pytest.mark.parking
def test_check_out(client) -> None:
    client_data = {"name": 'Peter2', "surname": 'Ivanov2', "credit_card": '6876 8989 66', "car_number": 'FF0909F'}
    client.post("/clients", data=client_data)

    parking_data = {"address": 'address2', "opened": True, "count_places": 5, "count_available_places": 2}
    client.post("/parkings", data=parking_data)

    check_in = {"client_id": 2, 'parking_id': 2, "time_in": datetime.utcnow()}
    client.post("/client_parkings", data=check_in)

    check_out = {"client_id": 2, 'parking_id': 2, "time_check_out": datetime.utcnow() + timedelta(hours=2)}
    resp = client.delete("/client_parkings", data=check_out)

    assert resp.status_code == 200


@pytest.mark.parking
def test_check_out_no_credit_cart(client) -> None:
    client_data = {"name": 'Peter2', "surname": 'Ivanov2'}
    client.post("/clients", data=client_data)

    parking_data = {"address": 'address2', "opened": True, "count_places": 5, "count_available_places": 2}
    client.post("/parkings", data=parking_data)

    check_in = {"client_id": 2, 'parking_id': 2, "time_in": datetime.utcnow()}
    client.post("/client_parkings", data=check_in)

    check_out = {"client_id": 2, 'parking_id': 2, "time_check_out": datetime.utcnow() + timedelta(hours=2)}
    resp = client.delete("/client_parkings", data=check_out)

    assert resp.status_code == 400


@pytest.mark.parametrize("route", ["/clients", "/clients/1"])
def test_route_status(client, route):
    rv = client.get(route)
    assert rv.status_code == 200
