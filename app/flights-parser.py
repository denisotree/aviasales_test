import os
import yaml
import datetime

import xml.etree.ElementTree as eTree

from pymongo import MongoClient
from pymongo import errors

from argparse import ArgumentParser

config = {
    'data-folder': 'data-source',  # Папка, из которой парсим файлы
    'db_host': 'flights_db',  # Хост базы данных
    'db_port': 27017,  # Порт базы данных
    'db_base': 'flights',  # База данных, куда пишем
    'db_collection': 'flights_collection'  # Коллекция, в которую пишем
}

'''
Данный скрипт можно запустить со следующими параметрами:

-c --config <path/to/config.yml> Конфиг для перезаписи параметров подключения к БД и источника файлов для парсинга
-a --address IP адрес базы данных
-p --port Порт базы данных
-f --folder Папка, из которой скрипт будет брать файлы для парсинга

'''

parser = ArgumentParser()

parser.add_argument(
    '-c', '--config', type=str, required=False,
    help="<path/to/config.yml> Конфиг для перезаписи параметров подключения к БД и источника файлов для парсинга"
)

parser.add_argument(
    '-a', '--address', type=str, required=False,
    help='IP адрес базы данных'
)

parser.add_argument(
    '-p', '--port', type=str, required=False,
    help='Порт базы данных'
)

parser.add_argument(
    '-f', '--folder', type=str, required=False,
    help='Папка, из которой скрипт будет брать файлы для парсинга'
)

args = parser.parse_args()

if args.config:
    with open(args.config) as f:
        config_file = yaml.safe_load(f)
        config.update(config_file or {})

if args.address:
    config['db_host'] = args.address

if args.port:
    config['db_port'] = args.port

if args.folder:
    config['data-folder'] = args.folder


# Это скрипт достает данные о перелете из xml и возвращает данные

def get_flight_details(flight):
    try:
        fare_basis = ''.join(flight.find('.//FareBasis').text.split())
        flight_data = {
            'company': flight.find('.//Carrier').text,
            'flight_number': flight.find('.//FlightNumber').text,
            'from': flight.find('.//Source').text,
            'to': flight.find('.//Destination').text,
            'depart_time': datetime.datetime.strptime(flight.find('.//DepartureTimeStamp').text,
                                                      '%Y-%m-%dT%H%M'),
            'arrival_time': datetime.datetime.strptime(flight.find('.//ArrivalTimeStamp').text,
                                                       '%Y-%m-%dT%H%M')
        }
        return fare_basis, flight_data
    except AttributeError:
        print('Некорректный файл')
        return False, False


'''
Этот скрипт при запуске парсит перелеты из папки data-parser и записывает их в MongoDB
'''


def flights_parser():
    # Собираем все файлы из папки для парсинга (по умолчанию data-source)
    parsed_files = [
        os.path.join(config['data-folder'], file)
        for file in os.listdir(config['data-folder'])
        if os.path.isfile(os.path.join(config['data-folder'], file)) and file.endswith('.xml')
    ]

    flights_json = []

    # Если файлы есть в папке, проходимся по каждому и собираем перелеты в готовый json объект
    if len(parsed_files):

        for file in parsed_files:

            tree = eTree.parse(file)
            root = tree.getroot()

            try:
                for flights_group in root.find('.//PricedItineraries'):
                    flights_group_data = dict()
                    flights_group_data['one_way_flight_details'] = []
                    flights_group_data['return_flight_details'] = []

                    # Собираем все по направлению "туда"
                    one_way = flights_group.find('.//OnwardPricedItinerary')
                    for flight in one_way.find('.//Flights'):
                        fare_basis, flight_data = get_flight_details(flight)
                        flights_group_data['one_way_flight_details'].append(flight_data)
                        flights_group_data['fare_basis'] = fare_basis
                        start_journey = flights_group_data['one_way_flight_details'][0]['depart_time']
                        end_journey = flights_group_data['one_way_flight_details'][-1]['arrival_time']
                        flight_duration = ((end_journey - start_journey).total_seconds())
                        flights_group_data['flight_duration'] = flight_duration

                    # Собираем все по направлению обратно
                    return_ = flights_group.find('.//ReturnPricedItinerary')
                    try:
                        for flight in return_.find('.//Flights'):
                            _, flight_data = get_flight_details(flight)
                            flights_group_data['return_flight_details'].append(flight_data)
                    except AttributeError:
                        pass

                    # Отдельно достаем цены и валюту
                    prices = flights_group.find('.//Pricing')
                    flights_group_data['currency'] = prices.attrib.get('currency')
                    flights_group_data['adult_price'] = float(prices.find(
                        './/ServiceCharges[@type="SingleAdult"][@ChargeType="TotalAmount"]'
                    ).text)

                    # Записываем данные по перелету в JSON
                    flights_json.append(flights_group_data)
            except TypeError:
                print('Некорректный файл')
    else:
        print('Папка с файлами для парсинга пуста')
        return flights_collection
    return flights_json


if __name__ == '__main__':

    # Коннектимся к БД
    try:
        client = MongoClient(
            'mongodb://' + config['db_host'] + ':' + str(config['db_port']),
            serverSelectionTimeoutMS=3000
        )
        db = client[config['db_base']]
        flights_collection = db[config['db_collection']]
        i = 0

        print(f'Запрашиваю данные')

        flights = flights_parser()

        # Заносим перелеты в базу, проверяя на дубликаты по fare_basis
        try:
            for fl in flights:
                if flights_collection.count_documents({'fare_basis': fl['fare_basis']}) == 0:
                    flights_collection.insert_one(fl)
                    i += 1
            client.close()
            print(f'В базу данных добавлено {i} записей')
        except TypeError:
            client.close()
            print('Не найдено ни одной записи о перелетах')
    except errors.ServerSelectionTimeoutError:
        print('Не удается подключиться к базе данных. Проверьте настойки.')
