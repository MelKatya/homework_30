from typing import Any, Dict

from sqlalchemy.orm import relationship

from .database import db, Model


class Client(Model):
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns}  # type: ignore[attr-defined]


class Parking(Model):
    __tablename__ = "parking"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name)
                for c in self.__table__.columns}  # type: ignore[attr-defined]


class ClientParking(Model):
    __tablename__ = "client_parking"
    __table_args__ = (
        db.UniqueConstraint("client_id",
                            "parking_id",
                            name="unique_client_parking"),
    )

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey(Client.id))
    parking_id = db.Column(db.Integer, db.ForeignKey(Parking.id))
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)

    parking = relationship("Parking", backref="client_parkings")
    client = relationship("Client", backref="client_parkings")

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "time_in": self.time_in.isoformat() if self.time_in else None,
            "time_out": self.time_out.isoformat() if self.time_out else None,
            "client": self.client.to_json(),
            "parking": self.parking.to_json(),
        }
