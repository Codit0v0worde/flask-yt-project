import os

from flask_assets import Bundle

from .functions import recursive_flattern_iterator

def get_filter(ext):
    return f"{ext}min"

def get_filename(route, tpl, ext, type):
    if type:
        return f"{route}_{tpl}_{ext}_defer"
    else:
        return f"{route}_{tpl}_{ext}"

def get_path(route, tpl, ext, type):
    if type:
        return f"gen/{route}/{tpl}/defer.{ext}"
    else:
        return f"gen/{route}/{tpl}/main.{ext}"

def get_bundle(route, tpl, ext, paths, type=False):
    """

    
    Функция возвращает словарь с настройками бандла для регистрации в Flask-Assets.
    :param route: название роута
    :param tpl: название шаблона
    :param ext: расширение (css/js)
    :param paths: список путей к исходным файлам
    :param type: если True, то генерируется "defer" версия, иначе "main"
    :return: словарь с ключами 'instance', 'name'
    """
    if route and tpl and ext:
        return {
            'instance': Bundle(
                *paths,
                output=get_path(route, tpl, ext, type),
                filters=get_filter(ext)
            ),
            'name': get_filename(route, tpl, ext, type)
        }
    else:
        raise ValueError("route, tpl и ext должны быть указаны")

def register_bundle(assets, bundle_data):
    """Регистрирует один бандл в assets"""
    assets.register(bundle_data['name'], bundle_data['instance'])

def register_bundles(assets, bundles):
    """Регистрирует все бандлы из структуры bundles"""
    for x in recursive_flattern_iterator(bundles):
        for bundle in x:
            register_bundle(assets, bundle)

# ------------------------------------------------------------
# Описание всех бандлов проекта
# ------------------------------------------------------------
bundles = {
    "post": {
        "all": {
            "css": [
                get_bundle('post', 'all', 'css', ['css/blocks/table.css'])
            ],
            "js": [
                get_bundle('post', 'all', 'js',
                           ['js/blocks/js1.js', 'js/blocks/js2.js', 'js/blocks/js3.js'])
            ]
        },
        "create": {},
        "update": {},
    },
    "user": {
        "login": {},
        "register": {},
    },
}



"""
    Функция возращает нужный Bundle(css/js для регистрации в главном файле приложения.
    Содержит пути до локальных исходников исходников css/js-файлов, сгруппированных друг с другом по использванию в шаблонах html.
    ---------------------------------------------------------------------------------------------
    1-й параметр route - название роута
    2-й параметр tpl - название шаблона html из папки /templates
    3-й параметр ext- расширение (css/js)
    4-й параметр paths(массив) - все пути к исходникам
    
    5-й параметр type  (опциональный) - используется только для JS.
    !!!Важно!!!Если нужен главный файл "main.js" параметр не указывать!
    Если нужен скрипт длительной загрузки "defer.js", передать булево значение True
    ---------------------------------------------------------------------------------------------
    """
