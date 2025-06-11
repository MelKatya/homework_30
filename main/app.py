from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flasgger import APISpec, Swagger
from flask import Flask

from .database import db
from .route import app_route
from .schemas import ClientParkingSchema, ClientSchema, ClientSchemaId, ParkingSchema


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///prod.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    spec = APISpec(
        title="ClientParkingList",
        version="1.0.0",
        openapi_version="2.0",
        plugins=[
            FlaskPlugin(),
            MarshmallowPlugin(),
        ],
    )

    template = spec.to_flasgger(
        app,
        definitions=[ClientSchema, ClientSchemaId, ParkingSchema, ClientParkingSchema],
    )
    Swagger(app, template=template)

    app.register_blueprint(app_route)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app
