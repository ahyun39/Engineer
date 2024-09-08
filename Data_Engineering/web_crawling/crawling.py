import requests
from bs4 import BeautifulSoup

def fetch_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_html(html):
    return BeautifulSoup(html, 'html.parser')

def extract_text_from_element(element):
    if element.name == 'img':
        return "IMAGE"
    elif element.name == 'a':
        return element.get_text(strip=True)
    elif element.name == 'strong':
        return extract_text_from_element(element)
    else:
        return element.get_text(strip=True)

def get_div_classes(soup):
    text_to_classes = []
    for div in soup.find_all('div', class_=lambda class_name: class_name and "plv" in class_name):
        text_elements = div.find_all(text=True, recursive=True)
        text = ' '.join(extract_text_from_element(el) for el in text_elements)
        text_to_classes.append(text)

    return text_to_classes

def main(url):
    html = fetch_page(url)
    soup = parse_html(html)
    text_to_classes = get_div_classes(soup)

    return text_to_classes

if __name__ == "__main__":
    url = "web url"
    data_list = main(url)