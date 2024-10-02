import requests
import http.cookiejar
from bs4 import BeautifulSoup
import re
import sys


# READING URLS FROM URL.TXT FILE AND REMOVING EMPTY SPACES
def read_urls(file_name: str):
    f = open(file_name, 'r')
    urls = [url.rstrip() for url in f]
    f.close()
    return urls


# SAVING PRICES OF OFFERED CARS
def save_in_file(car_list: list, file_name: str):
    f = open(file_name, 'w+')
    for car in car_list:
        [f.write(f'{n}:{v}\n') if n == list(car)[-1] else f.write(f'{n}:{v}\t\t') for n, v in car.items()]
    f.close()


if __name__ == '__main__':
    IN_FILE = 'urls.txt'
    OUT_FILE = 'data.tsv'

    car_urls_list = read_urls(file_name=IN_FILE)
    url_id = 0

    if len(sys.argv) > 1:
        try:
            required_offers = int(sys.argv[1])
        except ValueError:
            print('Please enter a number for the first program argument.', file=sys.stderr)
            sys.exit(1)
    else:
        required_offers = len(car_urls_list)

    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    car_offers = []
    with requests.session() as s:
        s.cookies = http.cookiejar.LWPCookieJar('ceny_aut.txt')
        s.headers.update({'User-Agent': UA})

        while len(car_offers) < required_offers and url_id != len(car_urls_list):
            url = car_urls_list[url_id]
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            car_name = soup.find('h1').text
            car_pricing = soup.find('div', {'class': re.compile('^StickyVehicleOverviewstyles__PriceWrap-zqcbn0-9*')})

            # Car price is None if the car has been purchased by someone
            if car_pricing is not None:
                car_offers.append({'URL': url, 'Car_name': car_name, 'Price': car_pricing.text})
            url_id += 1
    save_in_file(car_list=car_offers, file_name=OUT_FILE)
