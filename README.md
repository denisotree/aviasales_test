# Веб сервис для работы с данными перелетов

* Какие варианты перелёта из DXB в BKK мы получили?  

    Все варианты доступны по адресу /api/1.0/flights/  

* Самый дорогой/дешевый, быстрый/долгий и оптимальный варианты  

    Я решил не выделять самый дорогой/дешевый, быстрый/дорогой варианты,
    а просто реализовать сортировку по возрастанию/убыванию для кастомных столбцов.
    Таким образом первый элемент в результатирующем списке является искомым.
    А оствльные можно как-то еще использовать.  
    
    Варианты запросов:
    
    /?sort=adult_price&order=ASC — задано по умолчанию. Выведет перелеты по возрастанию цены.  
    /?order=DESC Выведет Выведет перелеты по убыванию цены.
    /?optim=1 Веведет оптимальный перелет

* В чём отличия между результатами двух запросов (изменение маршрутов/условий)?  
    
    Эту задачу я не успел реализовть — идея в том, чтобы сравнивать варианты перелетв проста,
    но встает вопрос как лучше выводить данные. Этого я пока не придумал.

### Установка и запуск

#### 1. Установка и запуск Docker
Если у вас уже установлен Docker, перейдите к следующему шагу

##### Ubuntu

Введите в терминал последовательно следующие команды:

`sudo apt-get update`

`sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D`

`sudo apt-add-repository 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'`

`sudo apt-get update`

`sudo apt-get install -y docker-engine`

Мы установили Docker, проверим, что процесс запущен

`sudo systemctl status docker`

##### MacOS

Загрузите [десктопное приложение Docker](https://download.docker.com/mac/stable/Docker.dmg) из официального репозитория

Установите, следуя указаниям системы

##### Windows

Загрузите [десктопное приложение Docker](https://download.docker.com/win/stable/Docker%20for%20Windows%20Installer.exe) из официального репозитория

Установите, следуя указаниям системы

#### 2. Установка docker-compose
Если у вас уже установлен docker-compose, перейдите к следующему шагу

##### Ubuntu

Введите в терминал последовательно следующие команды:

`curl -L https://github.com/docker/compose/releases/download/1.8.0/run.sh > /usr/local/bin/docker-compose`

`chmod +x /usr/local/bin/docker-compose`

Проверяем установку

`docker-compose --version`

##### MacOS

Docker compose уже включен в приложение docker

##### Windows

Docker compose уже включен в приложение docker

#### 3. Запуск

Теперь нужно создать файл окружения:

`nano .env`

И вставить туда переменные с логином и паролем от базы данных (логин и пароль установите свои):

`USER=dbuser`

`PASSWORD=dbpassword`

Осталась ерунда — нужно запустить контейнер следующей командой:

`docker-compose up --build -d`

И спарсить данные из файлов в папке data-source в базу командой:

`docker-compose exec -i flights_service python3 ./flights-parser.py`

Данные будут доступны на локальном хосте, 8000 порте

