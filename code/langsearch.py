import requests
from bs4 import BeautifulSoup
import spacy
nlp = spacy.load("en_core_web_sm")


def fetch_req(item):
    url = f"https://www.google.com/search?q=where+was+{item}+invented"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            searchres = soup.find(
                'div', {'class': 'BNeawe s3v9rd AP7Wnd'}).text
            return searchres
        except Exception as e:
            print('In langsearch: ', e)
    else:
        return ""
    return ""


def fetch_invention(data):
    doc = nlp(data)
    year = None
    place = None
    org = None
    for ent in doc.ents:
        print(f'text: {ent.text} , label: {ent.label_}')
        if ent.label_ == 'GPE' and place == None:
            place = ent.text
        if ent.label_ == 'DATE' and year == None:
            year = ent.text
        if ent.label_ == 'ORG' and org == None:
            org = ent.text
    return org if place == None else place, year


def get_res(item):
    data = fetch_req(item)
    place, year = fetch_invention(data)
    return place, year
