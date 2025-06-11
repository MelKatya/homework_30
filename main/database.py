from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model  # noqa: F811

db: SQLAlchemy = SQLAlchemy()
Model = db.Model  # type: ignore[misc, attr-defined]
