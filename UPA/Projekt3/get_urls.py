import requests
import http.cookiejar
from bs4 import BeautifulSoup
import re
import sys


# SAVING LIST OF URLS IN FILE
def save_in_file(url_list: list, file_name: str):
    f = open(file_name, 'w+')
    for url in url_list:
        f.write(url+'\n')
    f.close()


if __name__ == '__main__':
    PREPEND = 'https://www.cazoo.co.uk'
    URL = 'https://www.cazoo.co.uk/cars/'
    OUT_FILE = 'urls.txt'

    if len(sys.argv) > 1:
        try:
            required_urls = int(sys.argv[1])
        except ValueError:
            print('Please enter a number for the first program argument.', file=sys.stderr)
            sys.exit(1)
    else:
        required_urls = 300

    UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    urls_cnt = 0
    car_urls_list = []
    page = 1
    with requests.session() as s:
        s.cookies = http.cookiejar.LWPCookieJar('auta.txt')
        s.headers.update({'User-Agent': UA})

        while urls_cnt < required_urls:
            url = f'{URL}?page={page}'
            response = requests.get(url)

            soup = BeautifulSoup(response.content, 'html.parser')

            results = soup.find('ol', {'data-test-id': 'results-list', 'class': 'resultsstyles__ResultsList-sc-11kjmxu-0 ezjHRs'})
            # No more car offers available
            if results is None:
                break

            car_results = results.find_all('li', {'class': re.compile('^resultsstyles__ResultsListItem-sc-11kjmxu-1*')})
            # Eliminate ads results
            car_results = [c for c in car_results if c.find('li', {'class': re.compile('.*')})]

            for c in car_results:
                h = c.find('a', href=True)
                car_url = PREPEND+h['href']
                if car_url not in car_urls_list:
                    urls_cnt += 1
                    car_urls_list.append(car_url)
            page += 1

    save_in_file(url_list=car_urls_list[0:required_urls], file_name=OUT_FILE)
