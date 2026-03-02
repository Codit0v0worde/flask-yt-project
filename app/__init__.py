from flask import Flask, render_template
from .extensions import db, migrate, login_manager, assets
from .config import Config
from .bundles import bundles, register_bundles
from .routes.user import user
from .routes.post import post
from .routes.course import course
import pytz  # для работы с часовыми поясами

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(user)
    app.register_blueprint(post)
    app.register_blueprint(course)

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

    # Фильтр nl2br (замена переносов строк на <br>)
    def nl2br(value):
        if value:
            return value.replace('\n', '<br>')
        return ''
    app.jinja_env.filters['nl2br'] = nl2br

    # Фильтр для отображения дат в московском времени
    def moscow_datetime(value):
        if not value:
            return ''
        # Предполагаем, что дата в БД хранится в UTC (без таймзоны)
        utc_dt = pytz.utc.localize(value)
        moscow_dt = utc_dt.astimezone(pytz.timezone('Europe/Moscow'))
        return moscow_dt.strftime('%d.%m.%Y %H:%M')
    app.jinja_env.filters['moscow'] = moscow_datetime

    with app.app_context():
        db.create_all()

    # Обработчик ошибки 404
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    return app