import requests
from bs4 import BeautifulSoup

req = requests.get('https://www.concert.ru/place/')

soup = BeautifulSoup(req.text, 'lxml')

trs = soup.find('table').find_all('tr')

places = []

for tr in trs:
    places = tr.find_all('li')
    
    for place in places:
        if '(' not in place.text or ')' not in place.text:
            place_text :str = place.text.replace('\n', '')
            with open('places.txt', 'a', encoding='utf-8') as file:
                file.write(place.text)