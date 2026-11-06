# Message.Me

Учебный сайт вопросов и ответов для курса VK Education. В ветке `hw-1` находится статическая вёрстка, которую можно открыть через `public/index.html`. Ветка `hw-2` использует Django и демонстрационные данные.

## Локальный запуск

Нужен Python 3.12 или новее. Выполните в корне проекта.

**Windows (PowerShell)**

```powershell
py -3.12 -m venv .venv
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py runserver
```

**Linux и macOS**

```sh
python3 -m venv .venv
cp .env.example .env
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py runserver
```

## Запуск через Docker Compose

```sh
docker compose up --build
```

Откройте [Message.Me](http://localhost:8000/). Исходники подключаются из рабочей папки, а для `media/` используется отдельный том. Настройки локального запуска перечислены в `.env.example`.

| Адрес | Страница |
| --- | --- |
| `/` | Новые вопросы и поиск |
| `/hot/` | Популярные вопросы |
| `/tag/django/` | Вопросы по тегу |
| `/question/35/` | Вопрос и ответы |
| `/ask/` | Создание вопроса |
| `/login/` | Вход |
| `/signup/` | Регистрация |
| `/profile/` | Настройки профиля |

Параметр `page` переключает страницы списка или ответов. При некорректном значении открывается первая страница. Формы и голосование работают в режиме демонстрации.
