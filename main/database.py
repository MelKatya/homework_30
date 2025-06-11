from flask_sqlalchemy import SQLAlchemy

db: SQLAlchemy = SQLAlchemy()
Model = db.Model  # type: ignore[misc, attr-defined]
