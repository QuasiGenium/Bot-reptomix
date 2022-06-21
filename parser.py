import requests
import json
from bs4 import BeautifulSoup as parse


def parse_types(save=False):
    js = {}
    url = 'https://reptomix.com'
    r = requests.get(url)
    parse1 = parse(r.content, 'html.parser')
    js['type'], js['subtype'] = {}, {}

    for i in parse1.find_all(class_='mb-0 p-0 text-lg'):
        js['type'][i.text.strip()] = i.find('a').get('href').strip()
    for i in parse1.find_all(class_='rounded-md hover:bg-gray-50 text-base font-medium text-gray-900'):
        js['subtype'][i.text.strip()] = i.find('a').get('href').strip()

    if save:
        with open('types.json', 'w', encoding='utf-8') as file:
            json.dump(js, file, indent=4, ensure_ascii=False)

    return js


def all_of_type(type_: str, js=None):
    list_of_products = []
    if not js:
        with open('types.json', 'r', encoding='utf-8') as file:
            f = file.read()
            js = json.loads(f)

    url = ('https://reptomix.com' + js['type'][type_]) if type_ in js['type'].keys()\
        else ('https://reptomix.com' + js['subtype'][type_])

    r = requests.get(url)
    parse1 = parse(r.content, 'html.parser')
    for i in parse1.find_all(class_='card card-product'):
        a = {'name': i.find('a', class_="card-product-title mb-2 w-full").text.strip(),
             'price': int(''.join(i.find(class_='card-product-price-new').text.strip()[:-1].split('\xa0'))),
             'url': i.find('a', class_="card-product-title mb-2 w-full").get('href')}
        list_of_products.append(a)
    return list_of_products


def sort_between_prices(list_of_products, price_min=0, price_max=1_000_000_000_000):
    result = ''
    for i in list_of_products:
        if price_min <= i['price'] <= price_max:
            result += f'{i["name"]}\nЦена - {i["price"]}₽\nСсылка - https://reptomix.com{i["url"]}\n\n'
    return result[:-2]


if __name__ == '__main__':
    print(sort_between_prices(all_of_type('Змеи'), 15000, 25000))