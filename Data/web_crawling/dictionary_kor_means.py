# 네이버 한글 사전 크롤링

import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def get_first_definition(driver, query):
    url = f"https://ko.dict.naver.com/#/search?query={query}&range=all"
    driver.get(url)
    
    time.sleep(2)  # 페이지 로딩 대기

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    mean_items = soup.select_one('div.component_keyword.has-saving-function ul.mean_list li.mean_item p.mean')
    
    # word_class와 mark 클래스를 가진 span 태그는 제외하고 텍스트 추출
    for tag in mean_items.find_all(['span'], class_=['word_class', 'mark']):
        tag.decompose()
    
    # 남은 텍스트에서 공백 처리 및 정리
    text = mean_items.get_text()
    text = ' '.join(text.split())
    if mean_items:
        return text
    else:
        return None

def main():
    # 검색할 단어 리스트
    words = ["영수증", "사과", "학교", "컴퓨터", "강아지"]

    # 셀레니움 드라이버 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    results = []

    for word in words:
        print(f"검색 중: {word}")
        definition = get_first_definition(driver, word)
        if definition:
            print(f"  ➔ {definition}")
            results.append((word, definition))
        else:
            print(f"  ➔ 뜻을 찾을 수 없습니다.")
            results.append((word, "뜻을 찾을 수 없습니다."))

    driver.quit()

    # CSV로 저장
    csv_filename = 'words_meanings.csv'
    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['단어', '뜻'])  # 헤더
        writer.writerows(results)

if __name__ == "__main__":
    main()
