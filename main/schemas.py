from marshmallow import (
    Schema,
    ValidationError,
    fields,
    post_load,
    validates,
    validates_schema,
)

from .models import Client, ClientParking, Parking
from .utils import (
    check_client_exists,
    check_parking_exists,
    check_parking_open,
    get_client_by_id,
)


class ClientSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    surname = fields.Str(required=True)
    credit_card = fields.Str()
    car_number = fields.Str()

    @post_load
    def create_client(self, data: dict, **kwargs) -> Client:
        return Client(**data)


class ClientSchemaId(ClientSchema):
    id = fields.Int(required=True)

    @validates("id")
    def validate_id(self, id: int) -> None:
        client = get_client_by_id(id)
        if not client:
            raise ValidationError("Client with id={id} not found.".format(id=id))


class ParkingSchema(Schema):
    id = fields.Int(dump_only=True)
    address = fields.Str(required=True)
    opened = fields.Bool()
    count_places = fields.Int(required=True)
    count_available_places = fields.Int(required=True)

    @validates_schema
    def validate_place(self, data, **kwargs):
        if data["count_places"] < data["count_available_places"]:
            raise ValidationError(
                "The number of places must be "
                "greater than the number of available places",
                "error",
            )

    @post_load
    def create_parking(self, data: dict, **kwargs) -> Parking:
        return Parking(**data)


class ClientParkingSchema(Schema):
    id = fields.Int(dump_only=True)
    client_id = fields.Int(required=True)
    parking_id = fields.Int(required=True)
    time_in = fields.DateTime(dump_only=True)
    time_out = fields.DateTime(dump_only=True)

    @validates_schema
    def validate_check_parking_open(self, data, **kwargs):
        if not check_parking_open(data["parking_id"]):
            raise ValidationError("The parking is closed", "message")

    @validates_schema
    def validate_client_id(self, data, **kwargs):
        if not check_client_exists(data["client_id"]):
            raise ValidationError(
                f"There is no client with id={data['client_id']}", "error"
            )

    @validates_schema
    def validate_parking_id(self, data, **kwargs):
        if not check_parking_exists(data["parking_id"]):
            raise ValidationError(
                f"There is no parking with id={data['parking_id']}", "error"
            )

    @post_load
    def create_parking(self, data: dict, **kwargs) -> ClientParking:
        return ClientParking(**data)
