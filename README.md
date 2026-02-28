flask-yt-project/
├── app/                          # Основной код приложения
│   ├── models/                   # Модели БД (User, Post, Comment)
│   ├── routes/                   # Маршруты (user, post)
│   ├── templates/                # HTML-шаблоны (main, post, user)
│   ├── static/                    # Статика (css, js, uploads)
│   ├── forms.py                   # WTForms
│   ├── functions.py                # Вспомогательные функции (сохранение файлов)
│   ├── extensions.py               # Инициализация Flask-расширений
│   ├── bundles.py                  # Конфигурация Flask-Assets
│   └── __init__.py                 # Фабрика приложения
├── migrations/                    # Миграции БД (Alembic)
├── nginx/                         # Конфигурация Nginx для Docker
├── .dockerignore
├── .env                           # Переменные окружения (не в репозитории!)
├── .flaskenv                      # Переменные для Flask CLI
├── .gitignore
├── Dockerfile                     # Сборка Flask-приложения
├── app.ini                        # Конфигурация uWSGI
├── docker-compose.yml             # Оркестрация сервисов (postgres, flask, nginx)
├── requirements.txt               # Зависимости Python
└── README.md                      # Этот файл
