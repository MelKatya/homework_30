from typing import Any

import sqlalchemy
from flasgger import swag_from
from flask import Blueprint, request
from flask_restx import Api, Resource
from marshmallow import ValidationError

from .schemas import ClientParkingSchema, ClientSchema, ClientSchemaId, ParkingSchema
from .utils import (
    add_client,
    add_client_parking,
    add_parking,
    delete_client_parking,
    get_all_client,
    get_all_client_parkings,
    get_all_parkings,
    get_client_by_id,
)

app_route = Blueprint("routes", __name__)
api = Api(app_route, prefix="/api")


@api.route("/clients")
class ClientList(Resource):
    @swag_from("docs/clients_get.yml")
    def get(self) -> tuple[list[dict], int]:
        schema = ClientSchema()
        return schema.dump(get_all_client(), many=True), 200

    @swag_from("docs/clients_post.yml")
    def post(self) -> tuple[list[str] | list[Any] | dict[Any, Any], int]:
        raw_data = request.get_json()
        if raw_data is None:
            return {"error": "No data provided"}, 400

        data: dict[str, Any] = raw_data

        schema = ClientSchema()
        try:
            client = schema.load(data)

        except ValidationError as exc:
            return exc.messages, 400

        client = add_client(client)
        return schema.dump(client), 201


@api.route("/clients/<int:id>")
class BookListId(Resource):
    @swag_from("docs/clients_id_get.yml")
    def get(self, id) -> tuple[Any, int]:

        data = {"id": id}
        schema = ClientSchemaId()
        try:
            schema.load(data, partial=True)
        except ValidationError as exc:
            return exc.messages, 404

        client = get_client_by_id(id)
        return schema.dump(client), 200


@api.route("/parkings")
class ParkingList(Resource):
    @swag_from("docs/parkings_get.yml")
    def get(self) -> tuple[list[dict], int]:
        schema = ParkingSchema()
        return schema.dump(get_all_parkings(), many=True), 200

    @swag_from("docs/parkings_post.yml")
    def post(self) -> tuple[list[str] | list[Any] | dict[Any, Any], int]:
        raw_data = request.get_json()

        if raw_data is None:
            return {"error": "No data provided"}, 400

        data: dict[str, Any] = raw_data

        schema = ParkingSchema()
        try:
            parking = schema.load(data)

        except ValidationError as exc:
            return exc.messages, 400

        parking = add_parking(parking)
        return schema.dump(parking), 201


@api.route("/client_parkings")
class ClientParkingList(Resource):
    @swag_from("docs/client_parkings_get.yml")
    def get(self) -> tuple[list[dict], int]:
        schema = ClientParkingSchema()
        return schema.dump(get_all_client_parkings(), many=True), 200

    @swag_from("docs/client_parkings_post.yml")
    def post(self) -> tuple[Any, int] | tuple[str, int]:
        raw_data = request.get_json()

        if raw_data is None:
            return {"error": "No data provided"}, 400

        data: dict[str, Any] = raw_data

        schema = ClientParkingSchema()
        try:
            parking = schema.load(data)

        except ValidationError as exc:
            return exc.messages, 400

        try:
            parking = add_client_parking(parking)
            return schema.dump(parking), 201

        except sqlalchemy.exc.IntegrityError:
            return {"error": "The client is already parked " "in this parking lot"}, 400

        except ArithmeticError:
            return {"message": "There is no available places"}, 400

    @swag_from("docs/client_parkings_delete.yml")
    def delete(self) -> tuple[Any, int] | tuple[str, int]:
        raw_data = request.get_json()

        if raw_data is None:
            return {"error": "No data provided"}, 400

        data: dict[str, Any] = raw_data

        schema = ClientParkingSchema()
        try:
            schema.load(data)

        except ValidationError as exc:
            return exc.messages, 400

        try:
            payment = delete_client_parking(data["client_id"], data["parking_id"])

            if payment is not None:
                return {
                    "message": "Thanks for visiting. Park with us again",
                    "payment": f"{payment} of the money will be debited",
                }, 200

            else:
                return {
                    "error": f"The client with id={data['client_id']} "
                    f"didn't park "
                    f"in the parking lot with id={data['parking_id']}"
                }, 400

        except UserWarning:
            return {"message": "The client doesn't have a bank card"}, 400

        except KeyError:
            return {"message": "The client has already " "left this parking lot"}, 400
