from pymongo import MongoClient, ASCENDING, DESCENDING, errors
import flask
from flask import Flask, request, redirect
from bson.json_util import dumps, ObjectId

config = {
    'db_host': 'flights_db',  # Хост базы данных
    'db_port': 27017,  # Порт базы данных
    'db_base': 'flights',  # База данных, куда пишем
    'db_collection': 'flights_collection',  # Коллекция, в которую пишем
}

# Коннектимся к базе данных
try:
    client = MongoClient(
        f'mongodb://{config["db_host"]}:{str(config["db_port"])}',
        serverSelectionTimeoutMS=3000
    )
    db = client[config['db_base']]
    flights_collection = db[config['db_collection']]
except errors.ServerSelectionTimeoutError:
    print('Не удается подключиться к базе данных. Проверьте настойки.')


# Функция, делющая выборки с сортровкой из БД
def sort_flights(query, column, order):
    if order == "ASC":
        return flights_collection.find(query).sort(column, ASCENDING)
    elif order == "DESC":
        return flights_collection.find(query).sort(column, DESCENDING)


# Функция, находящая самый быстрый марщрут при самой низкой цене. Приоритет на низкой цене
def get_optim():
    return flights_collection.find_one(sort=[('adult_price', ASCENDING), ('flight_duration', ASCENDING)])


# Функция вывода данных в формате Json
def resp(code, data):
    return flask.Response(
        status=code,
        mimetype="application/json",
        response=data
    )


# Инициализируем Flask приложение
app = Flask(__name__)


@app.route('/')
def root():
    return redirect('/api/1.0/flights/')


'''
    Базовый роут api. По умолчанию выводит все перелеты, отсортированные по возрастанию цены.
    Можно модифицировать вывод следующими GET параметрами:
    sort=<имя столбца> — для выбора столбца, по которому производить сортировку
    order=<Направление> Направление сортировки — ASC или DESC
    optim=1 Задается отдельно ото всех. Выводит один перелет — наиболее оптимальный
'''
@app.route('/api/1.0/flights/')
def all_flights():
    sort_by = request.args.get('sort')
    order = request.args.get('order')
    optim = request.args.get('optim')
    if optim and not sort_by and not order:
        flights = get_optim()
    elif sort_by and order:
        flights = sort_flights({}, sort_by, order)
    elif sort_by and not order:
        flights = sort_flights({}, sort_by, 'ASC')
    elif not sort_by and order:
        flights = sort_flights({}, 'adult_price', order)
    else:
        flights = sort_flights({}, 'adult_price', 'ASC')
    return resp(200, dumps(flights))


'''
    Роут для вывода одного перелета по id
'''
@app.route('/api/1.0/flights/<flight_id>')
def one_flight(flight_id):
    flight = flights_collection.find_one({"_id": ObjectId(flight_id)})
    output = dumps(flight)
    return resp(200, output)


'''
    Тут должен быть роут для сравнения двух(или более) перелетов по id.
    ID передаются так:
    ids=<id_1>,<id_2>
    Я не успел придумать как лучше выводить разницу между перелетами. Потому функция не реализована.
'''
@app.route('/api/1.0/diff/')
def find_diff():
    diff_ids = request.args.get('ids').split(',')
    diff_flights = dumps(
        flights_collection.find(
            {"_id": {'$in': [ObjectId(diff_id) for diff_id in diff_ids]}}
        ))
    return resp(200, diff_flights)
