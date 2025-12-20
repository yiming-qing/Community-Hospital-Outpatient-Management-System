from flask import Flask
from .config import Config
from .extensions import cors, db, jwt
from .utils.errors import register_error_handlers

def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    try:
        from pathlib import Path
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    except Exception:
        pass

    app.config.from_object(config_object)
    app.json.ensure_ascii = False

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    from .utils.responses import error

    @jwt.unauthorized_loader
    def _unauthorized(msg: str):
        return error(msg or "Unauthorized", code="unauthorized", status=401)

    @jwt.invalid_token_loader
    def _invalid_token(msg: str):
        return error(msg or "Invalid token", code="invalid_token", status=401)

    @jwt.expired_token_loader
    def _expired_token(_jwt_header, _jwt_payload):
        return error("Token has expired", code="token_expired", status=401)

    from .api import register_blueprints
    register_blueprints(app)
    register_error_handlers(app)

    @app.get("/api/health")
    def health():
        return {"ok": True, "data": {"status": "up"}}

    @jwt.user_lookup_loader
    def _user_lookup_callback(_jwt_header, jwt_data):
        from .models import SysUser
        identity = jwt_data.get("sub")
        if identity is None:
            return None
        try:
            user_id = int(identity)
        except Exception:
            return None
        return SysUser.query.get(user_id)

    register_cli(app)

    if app.config.get("AUTO_SEED", False):
        try:
            with app.app_context():
                from .seed import ensure_seed_data

                ensure_seed_data()
        except Exception:
            app.logger.exception("AUTO_SEED failed")
    return app

def register_cli(app: Flask) -> None:
    import click

    from .seed import ensure_seed_data

    @app.cli.command("init-db")
    def init_db():
        """Create tables (for SQLite/dev)."""
        db.create_all()
        click.echo("OK: created tables.")

    @app.cli.command("seed")
    def seed():
        """Insert demo seed data (idempotent)."""
        ensure_seed_data()
        click.echo("OK: seeded data.")
