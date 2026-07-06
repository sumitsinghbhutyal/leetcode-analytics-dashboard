from flask import Flask, render_template
from .config import Config
from .extensions import db, login_manager, csrf
from .models.models import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    # csrf.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Blueprints
    from .routes.auth import auth_bp
    from .routes.dashboard import dashboard_bp
    from .routes.goals import goals_bp
    from .routes.leaderboard import leaderboard_bp
    from .routes.profile import profile_bp
    from .routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(goals_bp, url_prefix="/goals")
    app.register_blueprint(leaderboard_bp, url_prefix="/leaderboard")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Landing
    @app.route("/")
    def landing():
        return render_template("landing.html")

    # Create DB tables in dev
    with app.app_context():
        db.create_all()

    return app
