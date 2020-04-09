### News Parser - веб-приложение, собирающее данные с телеграм-, твиттер-каналов и RSS-лент.

Стэк
1. Технологии:
   1. PostgreSQL
   2. Python 3.6
   3. Docker
   4. JS
   5. Redis
   6. Nginx
1. Основные библиотеки и фреймворки:
   1. Django 2.0
   2. Django REST Framework
   3. Vue JS
   4. Vuex JS
   5. Telethon


Запуск
1. $ git clone git@gitlab.com:iteora/telegram-parser.git


```
Создаем сетку
docker network create -d bridge --subnet 192.168.0.0/24 --gateway 192.168.0.1 tg_parser
```

В файле docker-compose.yml в корне репозитория описаны основные настройки для запуска сервиса, там можно изменить пароли и названия БД в секции services/postgres, и/или исправить переменные окружения для конкретного случая:
* DB_DATABASE - название БД
* DB_USER - пользователь БД
* DB_PASSWORD
* DB_HOST - Hostname сервера с БД, обычно название docker контейнера, или localhost
* REDIS_HOST - Hostname сервера с Redis


Далее нужно скопировать src/app/local_settings_tpl.py в файл src/app/local_settings.py в котором исправить настройки для конкретного случая.


1. $ cd telegram-parser
2. $ cp src/app/local_settings_tpl.py src/app/local_settings.py


В файле src/app/local_settings.py нужно настроить доступы к API Telegram, выставить случайный и длинный SECRET_KEY, и включить DEBUG режим


1. $ docker-compose build
2. $ docker-compose run app python manage.py createsuperuser


Инициализирует базу данных и первого пользователя
Последним этапом настройки нужно в первый раз запустить сервис telegram_watcher чтобы залогиниться в Telegram и создать файл сессии


1. $ docker-compose run telegram_watcher
2. $ docker-compose up [-d]
3. $ docker-compose logs -f
выведет логи и будет следовать за ними
После запуска - на 8000 порту будет отвечать nginx из контейнера web. До него можно просто сделать proxy_pass http://127.0.0.1:8000; из nginx установленного в системе. Настройки виртуального хоста для контейнера с nginx находятся в файле web.conf.


В crontab нужно добавить следующую запись для запуска удаления старых сообщений:
0 0 * * * cd telegram_parser && docker-compose run app python manage.py delete_old_messages
________________


Разработка
1. Подготовка среды для разработки.
Предпочтительная ОС для разработки - Linux с установленным docker, node >= 9.8, npm.
Для использования webpack dev server’а при разработке  в шаблоне src/templates/index.html нужно закомментировать подключение скриптов и стилей, а в блок content дописать
<script src="http://127.0.0.1:8080/app.js"></script>


   1. Frontend:
Frontend приложения находится в папке frontend, исходный код в папке. Структура файлов в папке frontend/src с комментариями ниже, папки выделены жирным шрифтом:


```
|--- App.vue # компонент App, подключается в main.js
|   components # компоненты Vue
|   |--- Main.css # css
|   |--- Main.html # верстка
|   |--- Main.vue # основной компонент со всей логикой
|---  main.js # entrypoint webpack’а
|   store # Vuex
|   |---  api.js # экспортирует объект с методами взаимодействия для API
|   |---  index.js # экспортирует скофигурированный объект Vuex.Store
|   |    modules # модули Vuex
|   |   |---  feed.js
```

   1. Подготовка
$ npm i
   1. Запуск webpack dev server
        $ npm run dev
   1. Build
        $ npm run build
        Соберет css и javascript бандлы и положит в папку static/vue/.
________________


   1. Backend:
Исходный код находится в папке src. Структура файлов в папке src с комментариями ниже, папки выделены жирным шрифтом:


```
src
|--- __init__.py
|--- manage.py #  Manage скрипт Django.
|--- signals.py
|    app #  Проект Django.
|   |     db  #  Модифицированный драйвер postgresql для поддержки tsvector_field
|   |--- local_settings.py #  Файл с локальными настройками django
|   |--- local_settings_tpl.py #  Шаблон файла с локальными настройками django
|   |--- routing.py #  Настройки роутинга django channels (websocket, коммуникация django с воркерами)
|   |--- settings.py #  Настройки проекта Django.
|   |--- urls.py #  Файл настроек URL.
|   |--- wsgi.py
|    telegram_watcher # Приложение Django
|   |    admin # Тут описаны настройки админ-панели django
|   |   |--- __init__.py # тут импортируются классы ниже, тут же регистрируются модели
|   |   |--- site.py # class AdminSite
|   |   |--- feed.py # class FeedAdmin
|   |   |--- source.py # class UserSourceAdmin
|   |   |--- user.py # class MyUserAdmin
|   |    api # Тут описаны view классы для REST API
|   |   |--- feed.py # class FeedList
|   |   |--- message.py # view для получения сообщений из фидов, добавления и удаления в favorites и blacklist
|   |    consumers
|   |   |--- notifier.py  # Consumer для websocket
|   |    management
|   |   |    commands # manage.py скрипты. Запускаются - python manage.py <scriptname>
|   |   |   |--- __init__.py
|   |   |   |--- delete_old_messages.py # удаление сообщений старше указанного в local_settings  STORE_MESSAGES количества дней
|   |   |   |--- rss_watcher.py # startup скрипт для  запуска rss watcher’a
|   |   |   |--- telegram_watcher.py # startup скрипт для  запуска telegram watcher’a
|   |    migrations # миграции БД
|   |    models # модели данных
|   |   |--- __init__.py # imports
|   |   |--- mixins.py # class ModelDiffMixin для проверки объекта на изменение
|   |   |--- feed.py # модель Feed и through модель FeedMessage для ManyToMany отношения Feed-Message
|   |   |--- message.py # модель Message
|   |   |--- source.py # модель Source
|   |   |--- user.py # модель User и through модель UserSource для ManyToMany отношения User-Source
|   |    serializers # модели представления данных
|   |   |--- __init__.py # imports
|   |   |--- message.py # class MessageSerializer
|   |   |--- source.py # class SourceSerializer
|   |   |--- feed.py # class FeedSerializer
|   |    watcher # классы воркеров собирающих информацию
|   |   |--- __init__.py # imports
|   |   |--- rss.py # class RSSWatcher
|   |   |--- telegram.py # class TelegramWatcher
|   |--- __init__.py
|   |--- app.py
|    templates
|   |--- index.html  # шаблон главной страницы.
________________
```

   1. Backend: Модели данных:
   1. User
Модель пользователя, наследуется от Django модели AbstractUser
Создается командой:
docker-compose run app python manage.py createsuperuser
Или суперпользователем из приложения.
Содержит поля:
Строковые:
username: имя пользователя
password: пароль
first_name: имя
last_name: фамилия
email: E-mail
Даты:
date_joined: дата регистрации
last_login: дата последнего логина
Bool:
is_staff: наследие модели django - означает что пользователю разрешено заходить в админ-панель. На админке django основано все приложение - поэтому проверка отключена.
is_active: активность пользователя
Текстовые:
username_blacklist: разделенные переносом строки username пользователей из модели Message, чьи сообщения не будут показываться (во всех источниках).
В src/telegram_watcher/signals.py определен post_save сигнал, добавляющий созданного пользователя в группу с названием default, по ссылке tgg.iteora.com/auth/group можно редактировать права доступов к различным разделам для пользователей (не суперпользователей, они могут почти все и так)



   1. Source
Модель канала сообщений. Модель разделена на две, для четкого разделения между каналами созданными пользователем и логикой worker’ов с подключением и отключением от каналов.
   1. Source
        Модель канала в системе. Содержит поля:
        Строковые:
        type: значение - либо telegram или rss
        link: ссылка на канал. Для пользователей
В src/telegram_watcher/signals.py определены post_save и post_delete сигналы
   1. UserSource
в настройках называется My Sources, фактически является промежуточной таблицей для ManyToMany отношения User-Source,
содержит два внешних ключа: на модель User и на модель Source
________________


   1. Message
Модель сообщения.
Поля:
text - Текст сообщения
search - TSvectorField - индекс слов в сообщении именно по этому полю ищем сообщения, на уровне БД на этом поле висит несколько триггеров для автоматизации создания индекса, которые создаются автоматически средствами джанго.
source - Foreign Key к модели Source
username - Имя пользователя - отправителя сообщения. Используется для отображения и фильтрации пользователей
created - Дата создания экземпляра модели
date - Дата отправки сообщения
   1. Feed
   1. Feed
Модель фида. Поля:
name - Название фида (строка)
words - Слова для поиска разделенные переносом строки (текст)
last_retrieve - Дата последнего запроса сообщений из фида (дата)
user - FK к модели User
   1. FeedMessage
Промежуточная таблица для ManyToMany отношения Feed-Message
feed - FK к модели Feed
message - FK к модели Message
feed_source - FK к модели FeedSource - используется для запросов на каскадное удаление и оптимизаций поиска.
date - дата появления сообщения в фиде
   1. FeedSource
Промежуточная таблица для ManyToMany отношения Feed-Source
Поля:
feed - FK к модели Feed
source - FK к модели Source


celery_worker_1  | django.db.utils.InternalError: index "pg_toast_16506_index" contains unexpected zero page at block 4521
celery_worker_1  | HINT:  Please REINDEX it.
