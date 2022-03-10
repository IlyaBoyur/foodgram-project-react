![Foogram workflow](https://github.com/IlyaBoyur/foodgram-project-react/actions/workflows/main.yml/badge.svg)

# Продуктовый помощник Foodgram
На этом сервисе пользователи могут:
* публиковать рецепты;
* подписываться на публикации других пользователей;
* добавлять понравившиеся рецепты в список "Избранное";
* скачивать список продуктов-компонентов выбранных блюд.

<br>

## Технологии
Django, Django REST Framework, React.js, PostgreSQL, Gunicorn, Docker, nginx, Microsoft Azure, git

<br>

## Описание


Проект **Foodgram** собирает **рецепты** (**Recipe**) пользователей. Каждый рецепт содержит изображение, уникальные **тэги** (**Tag**), список из **ингредиентов** (**Ingredient**) и их количества. Пользователям доступно множество разных ингредиентов на выбор.

<br>

Пользователи могут добавить в избранное понравившиеся рецепты. Так все избранные рецепты будут доступны в одном месте. Пользователь может настроить свю *ленту новостей*: можно добавить в **подписки** (**Subscription**) любого автора и все его рецепты будут под рукой. 

<br>

Раздел "Cписок покупок" позволяет скачать сводный перечень всех ингредиентов для одного или нескольких рецептов.

<br>

## Локальный запуск проекта
### 1. Подготовьте окружение
- Установите [Docker](https://docs.docker.com/get-docker/)
- Установите [docker-compose](https://docs.docker.com/compose/install/)
- Перейдите в директорию проекта с файлом docker-compose.yaml (по умолчанию: infra)

### 2. Создайте файл переменных среды
Создайте в текущей папке файл .env со следующим содержимым:
```bash
SECRET_KEY=mysecretkey
DJANGO_DEBUG_VALUE=True
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### 3. Соберите и запустите контейнеры Docker
```bash
docker-compose up --build -d
```
Проект уже доступен! Осталось подготовить базу данных

### 4. Мигрируйте базу данных
```bash
docker-compose exec backend python manage.py migrate
```

### 5. Заполните базу данных тестовыми данными
Определите ID контейнера backend
```bash
docker-compose ps
```
Перенесите в контейнер файл с тестовыми данными и загрузите их в базу:
```bash
docker cp ../data/fixtures_backup.json <ID контейнера backend>:/
docker-compose exec backend python manage.py loaddata /fixtures_backup.json
```
Дождитесь окончания импорта.

Сообщение об успехе выглядит примерно так:
```bash
Installed 5504 object(s) from 1 fixture(s)
```

### 6. Соберите статические данные
```bash
docker-compose exec backend python manage.py collectstatic
```
Сообщение об успехе выглядит примерно так:
```bash
161 static files copied to '/code/backend_static'.
```

### 7. Профит! Проверьте в браузере
- Корневое представление приложения: http://127.0.0.1/
- Корневое представление API: http://127.0.0.1/api/
- Спецификация API: http://127.0.0.1/api/docs/
- Админка: http://127.0.0.1/admin
- Доступ к админке: 
  - login: admin@admin.su
  - password: admin

<br>

### Где посмотреть развернутый проект
- Размещение: Microsoft Azure
- [Ссылка на проект здесь](http://www.foodgram-project.ml/)
- Доступ к админке:
   - login: admin@admin.su
   - password: admin

<br>

### Планы по улучшению
* Добавить более подробный профиль пользователя
* Добавтиь бота для отправки списка покупок в мессенджеры
* Увеличить покрытие тестами: добавить проверку схем для моделей

<br>

### Авторы
- [Илья Боюр](https://github.com/IlyaBoyur)
