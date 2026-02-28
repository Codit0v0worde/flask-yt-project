from flask import Flask
from .extensions import db, migrate, login_manager, assets
from .config import Config
from .bundles import bundles, register_bundles
from .routes.user import user
from .routes.post import post

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(user)
    app.register_blueprint(post)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    assets.init_app(app)

    # LOGIN MANAGER
    login_manager.login_view = 'user.login'
    login_manager.login_message = 'Вам недоступна эта страница. ВЫ ДАЖЕ НЕ АВТОРИЗИРОВАНЫ!!! СНАЧАЛА ВОЙДИТЕ!!!'
    login_manager.login_message_category = 'info'

    # ASSETS
    register_bundles(assets, bundles)

    # Добавляем фильтр nl2br для Jinja2
    def nl2br(value):
        """Заменяет символы новой строки на <br>"""
        if value:
            return value.replace('\n', '<br>')
        return ''

    app.jinja_env.filters['nl2br'] = nl2br

    with app.app_context():
        db.create_all()

        #  404
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    return app