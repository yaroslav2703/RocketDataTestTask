"""
прежде чем выполнить скрипт, необходимо установить модули;
команды для установки мудулей:
    pip install requests
    pip install beautifulsoup4 lxml

результатом данного скрипта являются два json файла с данными:
    shops_info.json для https://www.mebelshara.ru/contacts
    offices_info.json для https://www.tui.ru/offices/
"""
import requests
from bs4 import BeautifulSoup
import json

PAGE_LINKS = [
    'https://www.mebelshara.ru/contacts',
]

API_LINKS = [
    'https://apigate.tui.ru/api/office/cities',
    'https://apigate.tui.ru/api/office/list'
]


def task1():
    """
    функция для получения данных с сайта https://www.mebelshara.ru/contacts
    """
    try:
        to_json = []
        first_page_response = requests.get(PAGE_LINKS[0], timeout=5)
        if first_page_response.status_code == 200:
            content = BeautifulSoup(first_page_response.content, 'lxml')
            address = content.select('div.address')[0].select('div.city-list.js-city-list')[0]
            city_list = [city_item.div for city_item in address.select('div.city-item')]
            for city_item in city_list:
                city_name = city_item.select('div.expand-block-header')[0].select('h4.js-city-name')[0].string
                shop_list = city_item.select('div.expand-block-content')[0].select('div.shop-list')[0]
                for shop in shop_list:
                    final_result_item = {
                        "address": city_name + ', ' + shop['data-shop-address'],
                        "latlon": [float(shop['data-shop-latitude']), float(shop['data-shop-longitude'])],
                        "name": shop['data-shop-name'],
                        "phones": shop['data-shop-phone'].split(','),
                        "working_hours": []
                    }
                    if 'Без выходных' in shop['data-shop-mode1']:
                        final_result_item['working_hours'].append("пн-вс: " + shop['data-shop-mode2'])
                    else:
                        final_result_item['working_hours'].append(shop['data-shop-mode1'])
                        final_result_item['working_hours'].append(shop['data-shop-mode2'])
                    to_json.append(final_result_item)

            with open('shops_info.json', 'w', encoding='utf-8') as f:
                json.dump(to_json, f, indent=4, ensure_ascii=False)
        else:
            print("1.status: " + first_page_response.status_code)
    except requests.Timeout as e:
        print("It is time to timeout")
        print(str(e))


def task2():
    """
    функция для получения данных с сайта https://www.tui.ru/offices/
    """
    try:
        all_offices = []
        to_json = []
        cities_response = requests.get(API_LINKS[0], timeout=5)
        if cities_response.status_code == 200:
            cities_response.encoding = 'utf-8'
            cities = cities_response.json()['cities']
            for city in cities:
                payload = {
                    'cityId': city['cityId'],
                }
                offices_response = requests.get(API_LINKS[1], params=payload, timeout=5)
                if offices_response.status_code == 200:
                    offices_response.encoding = 'utf-8'
                    offices = offices_response.json()['offices']
                    all_offices = all_offices + offices
                    for office in offices:
                        final_result_item = {
                            "address": office['address'],
                            "latlon": [float(office['latitude']), float(office['longitude'])],
                            "name": office['name'],
                            "phones": [phones['phone'] for phones in office['phones']],
                            "working_hours": []
                        }
                        hoursOfOperation = office['hoursOfOperation']
                        if not hoursOfOperation['workdays']['isDayOff']:
                            final_result_item['working_hours'].append(
                                'пн - пт ' + hoursOfOperation['workdays']['startStr'] + ' до ' +
                                hoursOfOperation['workdays']['endStr']
                            )
                        if not hoursOfOperation['saturday']['isDayOff']:
                            if not hoursOfOperation['sunday']['isDayOff']:
                                final_result_item['working_hours'].append(
                                    'сб - вс ' + hoursOfOperation['sunday']['startStr'] + ' до ' +
                                    hoursOfOperation['sunday']['endStr']
                                )
                            else:
                                final_result_item['working_hours'].append(
                                    'сб ' + hoursOfOperation['saturday']['startStr'] + ' до ' +
                                    hoursOfOperation['saturday']['endStr']
                                )

                        to_json.append(final_result_item)
                else:
                    print("2.1.status: " + offices_response.status_code)
            with open('offices_info.json', 'w', encoding='utf-8') as f:
                json.dump(to_json, f, indent=4, ensure_ascii=False)

        else:
            print("2.status: " + cities_response.status_code)
    except requests.Timeout as e:
        print("It is time to timeout")
        print(str(e))


if __name__ == '__main__':
    task1()
    task2()
