from flask import Flask

from .admin import bp as admin_bp
from .auth import bp as auth_bp
from .patient import bp as patient_bp
from .receptionist import bp as receptionist_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(receptionist_bp)
    app.register_blueprint(admin_bp)

